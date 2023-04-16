import socket
from _thread import *
import threading
import sys
from queue import Queue

# all above from from stdlib
from db.DB import DB

DB_PATH = "./db/app.db"

lock = threading.Lock()  # both main and threads need access to lock
# for now getting rid of use of lock, might need later so keeping variable

# may need to change this if need to be able to not user localhost
SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 1500
DEBUG = len(sys.argv) > 1 and sys.argv[1] == "DEBUG"


def splitlines_clrf(data: bytes) -> list[bytes]:
    """
    More guranteed safety that lines will split based on \r\n ONLY than build in splitlines
    """
    lines = []
    start = 0
    while True:
        end = data.find(b"\r\n", start)
        if end == -1:
            last_line = data[start:]
            if last_line:
                lines.append(last_line)
            break
        lines.append(data[start : end + 2])
        start = end + 2
    return lines


class User:
    username: str = None
    roomname: str = "test"


def handle_message(
    line: bytes,
    server: socket.socket,
    connections: dict[str, tuple[socket.socket, str]],
    db: DB,
    user: User,
):
    line: list[bytes] = line.split(b"--")
    # data = data.decode("ascii", errors="ignore").split("-")

    if line[0].decode("ascii") == "LOGIN":
        username = line[1].decode("ascii")
        password = line[2].decode("ascii")
        if db.check_user_credentials(username, password):
            server.send(b"OK\r\n")
            connections[username] = (server, "test")
            db.add_active_user(username)
            user.username = username
        else:
            server.send(b"ERROR\r\n")

    elif line[0].decode("ascii") == "SIGNUP":
        username = line[1].decode("ascii")
        password = line[2].decode("ascii")
        db.create_user(username, password)
        db.add_active_user(username)
        # TODO: send confirmation
        server.send(b"OK\r\n")

    elif line[0].decode("ascii") == "PAINT":
        message = line[1]
        roomname = line[2].decode(
            "ascii"
        )  # NOTE: sometimes this is wrong, prints testPAINT
        for connection, paint_roomname in connections.values():
            if paint_roomname == roomname:
                connection.send(b"PAINT--" + message + b"\r\n")
    elif line[0].decode("ascii") == "TEXT":
        message = line[1]
        roomname = line[2].decode(
            "ascii"
        )  # NOTE: sometimes this is wrong, prints testPAINT
        text = line[3]
        for connection, paint_roomname in connections.values():
            if paint_roomname == roomname:
                connection.send(b"TEXT--" + message + b"--" + text + b"\r\n")
    elif line[0].decode("ascii") == "CREATEROOM":
        roomname = line[1].decode("ascii")
        db.create_room(user.username, roomname)
    elif line[0].decode("ascii") == "JOINROOM":
        roomname = line[1].decode("ascii")
        username = user.username
        if db.room_joinable(roomname, username):
            db.join_room(username, roomname)
            connections[username] = (server, roomname)
            server.send(b"OK\r\n")
    elif line[0].decode("ascii") == "GETROOMS":
        # TODO: create get_active_users function in db
        roomlist = db.get_active_rooms()
        message = b""
        for room in roomlist:
            message += room.encode("ascii") + b"--"
        message = message[:-2]
        message += b"\r\n"
        server.send(message)
    elif line[0].decode("ascii") == "GETUSERS":
        # TODO: create get_user_list function in db
        userlist = db.get_active_users()
        message = b""
        for user in userlist:
            message += user.encode("ascii") + b"--"
        message = message[:-2]
        message += b"\r\n"
        server.send(message)
    elif line[0].decode("ascii") == "EXIT":
        server.send(b"EXIT\r\n")


def client_thread(
    server: socket.socket,
    addr,
    user: User,
    connections: dict[str, tuple[socket.socket, str]],
):
    """
    :param connections: Username to connection and roomname
    """
    db = DB(DB_PATH, debug=DEBUG)
    data = b""
    while True:
        try:
            data += server.recv(1024)
        except Exception:
            print(f"Disconnecting user : {addr[0]} : {addr[1]}")
            db.remove_active_user(user.username)
            connections.pop(user.username, "NO USER FOUND")
            # print_lock.release()
            break
        # lines = data.split(keepends=True)
        lines = splitlines_clrf(data)
        if len(lines) == 0:
            print(f"Disconnecting user : {addr[0]} : {addr[1]}")
            db.remove_active_user(user.username)
            connections.pop(user.username, "NO USER FOUND")
            # print_lock.release()
            break
        full_lines, last_line = lines[:-1], lines[-1]
        # print(f"full_lines: {full_lines}, last_line: {last_line}")
        for line in full_lines:
            handle_message(line[:-2], server, connections, db, user)
        if last_line.endswith(b"\r\n"):
            handle_message(last_line[:-2], server, connections, db, user)
            data = b""
        else:
            data = last_line

    # TODO: send confirmation
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
    connections: dict[str, tuple[socket.socket, str]] = {}
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
