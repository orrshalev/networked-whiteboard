import hashlib
import socket
import ssl
from _thread import *
import threading
import ssl

# all above from from stdlib
from db.DB import DB

print_lock = threading.Lock()  # both main and threads need access to lock

# may need to change this if need to be able to not user localhost
HOST = "127.0.0.1"
PORT = 1500


def thread_task(c: socket.socket, addr):
    while True:
        data = c.recv(1024)  

        if not data:
            print(f"Data not recieved correctly from : {addr[0]} : {addr[1]}")
            print_lock.release()
            break

        print(f"""New user info recieved: {data}""")

        # TODO: send confirmation
        # c.send()
    c.close()


def main():
    db = DB("./db/app.db")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TLS protocol
    server = ssl.wrap_socket(
        server, server_side=True, keyfile="./tls/host.key", certfile="./tls/host.cert"
    )

    server.bind((HOST, PORT))
    print(f"socket binded to port {PORT}")

    server.listen(
        100
    )  # will reject new connections when over 100 unaccepted connections active;
    # may need to do more to ensure can't have more than 100 active users
    print("Listening...")

    while True:
        c, addr = server.accept()

        print_lock.acquire()
        print(f"Connected to : {addr[0]} : {addr[1]}")

        start_new_thread(thread_task, (c, addr))

    db.close_connection()


if __name__ == "__main__":
    main()
