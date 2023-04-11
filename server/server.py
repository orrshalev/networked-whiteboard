import socket
import ssl
from _thread import *
import threading
import ssl

# all above from from stdlib
from db.DB import DB

DB_PATH = "./db/app.db"

lock = threading.Lock()  # both main and threads need access to lock
# for now getting rid of use of lock, might need later so keeping variable

# may need to change this if need to be able to not user localhost
SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 1500


def thread_task(c: socket.socket, addr):
    db = DB(DB_PATH)
    while True:
        data = c.recv(1024)

        if not data:
            print(f"Data not recieved correctly from : {addr[0]} : {addr[1]}")
            # print_lock.release()
            break

        # TODO: Maybe do error handeling
        data = data.decode("ascii").split("-")

        if data[0] == "LOGIN":
            username = data[1]
            password = data[2]
            if db.check_user_credentials(username, password):
                c.send(b"OK-")
                break
            else:
                c.send(b"ERROR")
                break

        elif data[0] == "SIGNUP":
            username = data[1]
            password = data[2]
            db.create_user(username, password)
            db.close_connection()
            break
            # TODO: send confirmation

        elif data[0] == "PAINT":
            message = data[1]
            roomname = data[2]
            ## Locks likely needed, can test without
            lock.acquire()
            db.update_room_pixel(roomname, message)
            lock.release()
            c.send(b'OK-')

        # TODO: send confirmation
        # c.send()
    c.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TLS protocol
    server = ssl.wrap_socket(
        server, server_side=True, keyfile="./tls/host.key", certfile="./tls/host.cert"
    )

    server.bind((SERVER_HOST, SERVER_PORT))
    print(f"socket binded to port {SERVER_PORT}")

    server.listen(
        100
    )  # will reject new connections when over 100 unaccepted connections active;
    # may need to do more to ensure can't have more than 100 active users
    print("Listening...")

    while True:
        c, addr = server.accept()

        # print_lock.acquire()
        print(f"Connected to : {addr[0]} : {addr[1]}")

        start_new_thread(
            thread_task,
            (
                c,
                addr,
            ),
        )


if __name__ == "__main__":
    main()