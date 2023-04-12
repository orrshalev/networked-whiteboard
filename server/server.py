import socket
import ssl
from _thread import *
import threading
import ssl
from queue import Queue

# all above from from stdlib
from db.DB import DB

DB_PATH = "./db/app.db"

lock = threading.Lock()  # both main and threads need access to lock
# for now getting rid of use of lock, might need later so keeping variable

# may need to change this if need to be able to not user localhost
SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 1500

def paint_handler(server: socket.socket, addr, q: Queue):
    pass

def client_thread(server: socket.socket, addr, q: Queue):
    db = DB(DB_PATH)
    while True:
        data = server.recv(1024)

        if not data:
            print(f"Data not recieved correctly from : {addr[0]} : {addr[1]}")
            # print_lock.release()
            break

        # TODO: Maybe do error handeling
        data = data.split(b"-")
        # data = data.decode("ascii", errors="ignore").split("-")

        if data[0].decode('ascii') == "LOGIN":
            username = data[1].decode("ascii")
            password = data[2].decode("ascii")
            if db.check_user_credentials(username, password):
                c.send(b"OK-")
            else:
                c.send(b"ERROR")

        elif data[0].decode("ascii") == "SIGNUP":
            username = data[1].decode("ascii")
            password = data[2].decode("ascii")
            db.create_user(username, password)
            # TODO: send confirmation
            server.send(b"OK-")

        elif data[0].decode('ascii') == "PAINT":
            message = data[1]
            roomname = data[2].decode("ascii")
            ## Locks likely needed, can test without
            #lock.acquire()
            db.update_room_pixel(roomname, message)
            #lock.release()
            print(f"PAINT RECIEVED, message is: {message}, roomname is {roomname}")
            TEST_PAINT_MESSAGE = b"PAINT-" + (100).to_bytes(2, "big") + (100).to_bytes(2, "big") + (1).to_bytes(1, "big")
            server.send(TEST_PAINT_MESSAGE)

        # TODO: send confirmation
        # c.send()
    server.close()


def main():
    print(f"SERVER IP ADDRESS IS {SERVER_HOST}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TLS protocol
    # server = ssl.wrap_socket(
    #     server, server_side=True, keyfile="./tls/host.key", certfile="./tls/host.cert"
    # )

    server.bind((SERVER_HOST, SERVER_PORT))
    print(f"socket binded to port {SERVER_PORT}")

    server.listen(
        100
    )  # will reject new connections when over 100 unaccepted connections active;
    # may need to do more to ensure can't have more than 100 active users
    print("Listening...")
    # paint_handler goes outside while loop; should only have 1 exist
    while True:
        c, addr = server.accept()

        # print_lock.acquire()
        print(f"Connected to : {addr[0]} : {addr[1]}")

        start_new_thread(
            client_thread,
            (
                c,
                addr,
            ),
        )


if __name__ == "__main__":
    main()