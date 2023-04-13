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

# define a class to hold user data
class User:
    username: str = None
    roomname: str = "test"



def client_thread(
        server: socket.socket, addr, user: User, connections: dict[str, tuple[socket.socket, str]]
):
    """ Handles a client thread
    :param connections: Username to connection and roomname
    """
    db = DB(DB_PATH)
    
    # run forever
    while True:
        data = server.recv(1024)

        if not data:
            print(f"Data not recieved correctly from : {addr[0]} : {addr[1]}")
            # print_lock.release()
            break

        # TODO: Maybe do error handeling
        data = data.split(b"-")
        # data = data.decode("ascii", errors="ignore").split("-")

        # if user is not logged in, only allow login/signup
        if data[0].decode("ascii") == "LOGIN":
            username = data[1].decode("ascii")
            password = data[2].decode("ascii")
            if db.check_user_credentials(username, password):
                server.send(b"OK-")
                connections[username] = (server, "test")
            else:
                server.send(b"ERROR")

        elif data[0].decode("ascii") == "SIGNUP":
            username = data[1].decode("ascii")
            password = data[2].decode("ascii")
            db.create_user(username, password)
            # TODO: send confirmation
            server.send(b"OK-")

        elif data[0].decode("ascii") == "PAINT":
            message = data[1]
            roomname = data[2].decode(
                "ascii"
            )  # NOTE: sometimes this is wrong, prints testPAINT
            ## Locks likely needed, can test without
            # lock.acquire()
            db.update_room_pixel(roomname, message)
            # lock.release()
            print(f"PAINT RECIEVED, message is: {message}, roomname is {roomname}")
            # This is a reminder why I needed to implement a condition:
            # server.send(b"PAINT-" + message)
            for connection, paint_roomname in connections.values():
                if paint_roomname == roomname:
                    connection.send(b"PAINT-" + message)
                

        # TODO: send confirmation
        # c.send()
    server.close()


def main():
    """ Main function for server """
    print(f"SERVER IP ADDRESS IS {SERVER_HOST}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TLS protocol
    # server = ssl.wrap_socket(
    #     server, server_side=True, keyfile="./tls/host.key", certfile="./tls/host.cert"
    # )

    # bind socket to port
    server.bind((SERVER_HOST, SERVER_PORT))
    print(f"socket binded to port {SERVER_PORT}")

    # put the socket into listening mode
    server.listen(
        100
    )  # will reject new connections when over 100 unaccepted connections active;
    # may need to do more to ensure can't have more than 100 active users
    print("Listening...")
    # paint_handler goes outside while loop; should only have 1 exist
    connections: dict[str, tuple[socket.socket, str]] = {}
    
    # a forever loop until client wants to exit
    while True:
        connection, addr = server.accept()
        user: User = User()

        # print_lock.acquire()
        print(f"Connected to : {addr[0]} : {addr[1]}")

        client_listener = threading.Thread(
            target=client_thread, args=(connection, addr, user, connections)
        )
        client_listener.start()


if __name__ == "__main__":
    main()
