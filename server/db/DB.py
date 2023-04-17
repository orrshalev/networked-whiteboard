import sqlite3
import socket
import os
import hashlib
import sys
import datetime

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAX_REGISTERED_USERS = 150


class DB:
    """ This class is responsible for all database operations """
    def __init__(self, db_file: str, debug=False):
        """
        establish persistent connection
        """
        self.conn = sqlite3.connect(
            db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.DEBUG = debug
        self._debug_print()

    def _debug_print(self):
        if self.DEBUG:
            print("Here are the open rooms:\n")
            self._show_rooms_table()
            print()
            print("Here are the registered users:\n")
            self.select_all_users()
            print()

    def _raw_command(self, sql: str) -> None:
        """Will execute any command given; do not use outside of file sql: SQLite query
        :return:
        """
        c = self.conn.cursor()
        c.execute(sql)

    def update_exit_time(self, username: str):
        """ Update the exit time of a user """
        c = self.conn.cursor()
        select_statement = """SELECT * FROM rooms
                              WHERE host = ? ;"""
        c.execute(select_statement, (username,))
        rows = c.fetchall()
        if len(rows) == 0:
            return

        update_statement = """UPDATE rooms
                              SET closed_at = ?
                              WHERE host = ? ;"""
        c.execute(update_statement, (datetime.datetime.now(), username))
        self.conn.commit()
        self._debug_print()

    def _create_rooms_table(self):
        """ Create the rooms table if it doesn't exist"""
        c = self.conn.cursor()
        rooms_schema = """CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY,
                    roomname text NOT NULL,
                    host text NOT NULL,
                    password text,
                    salt text,
                    closed_at timestamp,
                    FOREIGN KEY(host) REFERENCES users(username)
                )"""
        c.execute(rooms_schema)

    def _delete_rooms_table(self):
        c = self.conn.cursor()
        drop_rooms_table = "DROP TABLE rooms"
        c.execute(drop_rooms_table)

    def _create_active_user_table(self):
        c = self.conn.cursor()
        active_users_scehma = """CREATE TABLE IF NOT EXISTS active_users (
                                 id INTEGER PRIMARY KEY,
                                 username text NOT NULL,
                                 roomname text
                )"""
        c.execute(active_users_scehma)

    def add_active_user(self, username: str):
        c = self.conn.cursor()
        insert_statement = """INSERT INTO active_users(username)
                              VALUES (?)"""
        c.execute(insert_statement, (username,))
        self.conn.commit()
        self._debug_print()

    def _select_all_active_users(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM active_users")

        rows = c.fetchall()

        for row in rows:
            print(row)

    def remove_active_user(self, username: str):
        c = self.conn.cursor()
        delete_statement = """DELETE FROM active_users
                              WHERE username = ? ;"""
        c.execute(delete_statement, (username,))
        self.conn.commit()

        select_statement = """SELECT * FROM rooms
                              WHERE host = ?"""
        c.execute(select_statement, (username,))
        rows = c.fetchall()
        if len(rows) == 0:
            return

        insert_statement = """UPDATE rooms
                              SET closed_at = ?
                              WHERE host = ? ;"""
        c.execute(insert_statement, (datetime.datetime.now(), username))
        self.conn.commit()
        self._debug_print()

    def join_room(self, username: str, roomname: str) -> bool:
        c = self.conn.cursor()
        update_statement = """UPDATE active_users
                              SET roomname = ?
                              WHERE username = ? ;"""
        c.execute(update_statement, (roomname, username))
        self.conn.commit()
        return True

    def get_active_users(self) -> list[str]:
        c = self.conn.cursor()
        select_statement = """SELECT username 
                               FROM active_users
                               """
        c.execute(select_statement)
        rows = c.fetchall()
        return [row[0] for row in rows]

    def get_active_rooms(self):
        c = self.conn.cursor()
        select_statement = """SELECT roomname 
                               FROM rooms
                               """
        c.execute(select_statement)
        rows = c.fetchall()
        return [row[0] for row in rows]

    def create_room(self, username: str, roomname: str, password: str = None):
        """
        Create a new room assigned to a host (user that created room)
        :param username: username of host
        :param roomname: room name (visible to others)
        """
        try:
            room_schema = f"""CREATE TABLE {roomname} (
                        x INTEGER NOT NULL,
                        y INTEGER NOT NULL,
                        R INTEGER NOT NULL,
                        B INTEGER NOT NULL,
                        G INTEGER NOT NULL,
                        A INTEGER NOT NULL,
                        PRIMARY KEY (x, y)
                    );
            """
            c = self.conn.cursor()
            c.execute(room_schema)
            table_values = f"""INSERT INTO {roomname} VALUES (?, ?, ?, ?, ?, ?)"""
            for x in range(WINDOW_WIDTH):
                for y in range(WINDOW_HEIGHT):
                    c.execute(
                        table_values, (x, y, 255, 255, 255, 255)
                    )  # Insert white to all
            self.conn.commit()
        except Exception:
            print(f"WARNING: ROOM WITH NAME {roomname} ALREADY EXISTS")

        if password:
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
            add_to_rooms_table = (
                "INSERT INTO rooms(roomname, host, password, salt) VALUES (?, ?, ?, ?)"
                if password
                else "INSERT INTO rooms(roomname, host) VALUES (?, ?)"
            )
            c.execute(add_to_rooms_table, (roomname, username, key, salt))
        else:
            add_to_rooms_table = "INSERT INTO rooms(roomname, host) VALUES (?, ?)"
            c.execute(add_to_rooms_table, (roomname, username))
        self.conn.commit()
        self._debug_print()

    def update_room_pixel(self, roomname: str, paint_message: bytes) -> None:
        
        """ Update the pixel in the room table """
        c = self.conn.cursor()
        update_statement = f"""UPDATE {roomname}
                               SET R = ?,
                                   G = ?,
                                   B = ?,
                                   A = ?
                               WHERE x = ? AND y = ?"""
        x = int.from_bytes(paint_message[0:2], byteorder="big")
        y = int.from_bytes(paint_message[2:4], byteorder="big")
        R = int.from_bytes(paint_message[4:5], byteorder="big")
        G = int.from_bytes(paint_message[5:6], byteorder="big")
        B = int.from_bytes(paint_message[6:7], byteorder="big")
        A = int.from_bytes(paint_message[7:8], byteorder="big")
        c.execute(update_statement, (R, G, B, A, x, y))
        self.conn.commit()

    def send_room_pixels(self, roomname: str, connection: socket.socket) -> None:
        """ Send the pixel to the client """
        c = self.conn.cursor()
        select_statement = f"""SELECT X, Y, R, B, G, A
                               FROM {roomname}"""
        c.execute(select_statement)
        rows = c.fetchall()
        for X, Y, R, B, G, A in rows:
            X_bytes = X.to_bytes(2, byteorder="big")
            Y_bytes = Y.to_bytes(2, byteorder="big")
            R_bytes = R.to_bytes(1, byteorder="big")
            G_bytes = G.to_bytes(1, byteorder="big")
            B_bytes = B.to_bytes(1, byteorder="big")
            A_bytes = A.to_bytes(1, byteorder="big")
            connection.send(b"PIXEL_RGB--" + X_bytes + Y_bytes + R_bytes + G_bytes + B_bytes + A_bytes + b"\r\n")
        
        

    def _check_room(self, roomname: str):
        """ Check if room exists """
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM {roomname}")

        rows = c.fetchall()

        for row in rows:
            print(row)
        print(f"Number of pixels: {len(rows)}")

    def host_disconnected(self, roomname: str):
        """ Set the room to recovery mode """
        c = self.conn.cursor()
        update_statement = """UPDATE rooms
                              SET closed_at = ?
                              WHERE roomname = ?"""
        c.execute(update_statement, (datetime.datetime.now(), roomname))
        self.conn.commit()

    def room_paintable(self, roomname: str) -> bool:
        """ Check if room is in recovery mode """
        c = self.conn.cursor()
        select_statement = """SELECT closed_at
                              FROM rooms
                              WHERE roomname = ? ;"""
        c.execute(select_statement, (roomname,))
        vals = c.fetchall()
        for val in vals:
            print(f"DEBUG STATEMENT: {val}")

        if len(vals) == 0:
            print("WARNING: ROOM NOT FOUND")
            return False
        if vals[0] is None:
            return True

        return False  # room is in recovery mode

    def recover_room(self, roomname: str, username: str, connection: socket.socket):
        self.join_room(username, roomname)

    def room_joinable(self, roomname: str, username: str, password: str = None) -> bool:
        c = self.conn.cursor()
        # check if room exists
        select_statement = """SELECT closed_at, host, password, salt
                              FROM rooms
                              WHERE roomname = ? ;"""
        c.execute(select_statement, (roomname,))
        vals = c.fetchall()

        if len(vals) == 0:
            print("WARNING: ROOM NOT FOUND")
            return False

        # check timeout and password
        key: str = vals[0][2]
        salt: str = vals[0][3]
        time: datetime.datetime = vals[0][0]
        SECONDS_IN_HOUR = 3600
        if password and not key:
            return False
        if password:
            new_key = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, 100000
            )
            if time:
                time_passed: datetime.timedelta = datetime.datetime.now() - time
                return (
                    key == new_key
                    and time_passed.total_seconds() < SECONDS_IN_HOUR
                )
            else:
                return key == new_key

        if time is None:
            return True

        time_passed: datetime.timedelta = datetime.datetime.now() - time
        # not timed out
        if time_passed.total_seconds() < SECONDS_IN_HOUR and username == vals[0][1]:
            return True

        # timed out
        drop_statement = f"""DROP TABLE IF EXISTS {roomname} ;"""
        c.execute(drop_statement)
        delete_statement = """DELETE FROM rooms
                              WHERE roomname = ? ;"""
        c.execute(delete_statement, (roomname,))
        self.conn.commit()
        update_statement = """UPDATE active_users
                              set roomname = NULL
                              WHERE roomname = ? ;"""
        c.execute(update_statement, (roomname,))
        return False

    def close_room(self, roomname: str):
        """
        Drops table with roomname
        :param roomname:
        """
        drop_room = f"""DROP TABLE IF EXISTS {roomname} ; """
        c = self.conn.cursor()
        c.execute(drop_room)

        drop_from_room_table = """DELETE FROM rooms
                                  WHERE roomname = ?"""
        c.execute(drop_from_room_table, (roomname,))
        self.conn.commit()

    def _show_rooms_table(self):
        select_statement = "SELECT * FROM rooms"
        c = self.conn.cursor()
        c.execute(select_statement)

        rows = c.fetchall()

        for row in rows:
            print(row)

    def create_user(self, username: str, password: str) -> int:
        """
        Create a new user into the users table
        :param user[0]: username
        :param user[1]: non-hashed password
        :return: user id
        """
        c = self.conn.cursor()
        select_statement = """SELECT * FROM users"""
        c.execute(select_statement)
        rows = c.fetchall()
        if len(rows) > MAX_REGISTERED_USERS:
            print("WARNING: MAXIMUM USERS ALLOWED TO REGISTER REACHED")
            return
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        sql = """ INSERT INTO users(username, password, salt)
                  VALUES(?,?,?) """
        c = self.conn.cursor()
        c.execute(sql, (username, key, salt))
        self.conn.commit()
        print(f"User {username} created")
        return c.lastrowid

    def select_all_users(self) -> list[str]:
        """
        Query all rows in the users table
        :return:
        """
        c = self.conn.cursor()
        c.execute("SELECT username FROM users")

        rows = c.fetchall()

        return [row[0] for row in rows]

    def check_if_owner(self, username: str, roomname: str):
        c = self.conn.cursor()
        select_statement = """SELECT * 
                              FROM rooms
                              WHERE host = ?
                              AND roomname = ? ;"""
        c.execute(select_statement, (username, roomname))
        rows = c.fetchall()
        return len(rows) != 0

    def check_user_credentials(self, username: str, password: str) -> bool:
        """
        Check if user credentials match a value in users table
        """
        c = self.conn.cursor()
        c.execute(
            """ SELECT *
                        FROM users
                        WHERE username=?""",
            (username,),
        )

        rows = c.fetchall()

        # No user with this username
        if len(rows) == 0:
            return False

        user = rows[0]
        key = user[2]
        salt = user[3]
        new_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return key == new_key

    def close_connection(self):
        """
        Needs to be done when program exits if DB was initialized
        """
        self.conn.close()


def main():
    """
    Can set the state of the DB upon initialization of docker image from Here
    using CLI
    """

    def check_arg(length: int, arg: str):
        return len(sys.argv) == length and sys.argv[1] == arg

    database = "./app.db"
    db = DB(database)

    if check_arg(2, "CREATE_USER_TABLE"):
        user_schema = """CREATE TABLE IF NOT EXISTS users (
                    id integer PRIMARY KEY,
                    username text NOT NULL,
                    password text NOT NULL,
                    salt     text NOT NULL
                ); """
        db._raw_command(user_schema)
    elif check_arg(2, "DELETE_USER_TABLE"):
        delete_user_table = """DROP TABLE IF EXISTS users;"""
        db._raw_command(delete_user_table)
    elif check_arg(4, "ADD_USER"):
        user_id = db.create_user(sys.argv[2], sys.argv[3])
    elif check_arg(2, "SELECT_ALL_USERS"):
        db.select_all_users()
    elif check_arg(4, "CHECK_USER"):
        user_exists = db.check_user_credentials(sys.argv[2], sys.argv[3])
        if user_exists:
            print(f"User with credentials {sys.argv[2]} {sys.argv[3]} in table")
        else:
            print(f"User with credentials {sys.argv[2]} {sys.argv[3]} not found")
    elif check_arg(4, "ADD_ROOM"):
        db.create_room(sys.argv[2], sys.argv[3])
    elif check_arg(3, "DELETE_ROOM"):
        db.close_room(sys.argv[2])
    elif check_arg(3, "SHOW_ROOM"):
        db._check_room(sys.argv[2])
    elif check_arg(2, "CREATE_ROOMS_TABLE"):
        db._create_rooms_table()
    elif check_arg(2, "SHOW_ROOMS_TABLE"):
        db._show_rooms_table()
    elif check_arg(2, "DELETE_ROOMS_TABLE"):
        db._delete_rooms_table()
    elif check_arg(6, "UPDATE_PIXEL"):
        # note that this conversion is not the same as what you will use in real scenario
        message = (
            int(sys.argv[3]).to_bytes(2, byteorder="big")
            + int(sys.argv[4]).to_bytes(2, byteorder="big")
            + int(sys.argv[5]).to_bytes(1, byteorder="big")
        )
        db.update_room_pixel(sys.argv[2], message)
    elif check_arg(5, "GET_PIXEL"):
        db._get_room_pixel(sys.argv[2], sys.argv[3], sys.argv[4])
    elif check_arg(2, "CREATE_ACTIVE_USER_TABLE"):
        db._create_active_user_table()

    else:
        explainer = """
            RUN FROM db DIRECTORY
            python ./DB.py CREATE_USER_TABLE
            python ./DB.py ADD_USER <username> <password>
            python ./DB.py SELECT_ALL_USERS
            I don't feel like writing the rest LOL 
            Read the end of this Python file to see options
        """
        raise Exception(explainer)

    db.close_connection()


if __name__ == "__main__":
    main()
