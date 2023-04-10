import sqlite3
import os
import hashlib
import sys
import datetime

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


# TODO: limit # of users that can be created
class DB:
    def __init__(self, db_file: str):
        """
        establish persistent connection
        """
        self.conn = sqlite3.connect(db_file)

    def _conversions():
        """
        Useless function; delete later
        """
        num = 5
        two_bytes = num.to_bytes(2, byteorder="big")
        back_to_num = int.from_bytes(two_bytes, byteorder="big")

    def _raw_command(self, sql: str) -> None:
        """Will execute any command given; do not use outside of file
        sql: SQLite query
        :return:
        """
        c = self.conn.cursor()
        c.execute(sql)

    def _create_rooms_table(self):
        c = self.conn.cursor()
        rooms_schema = """CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY,
                    roomname text NOT NULL,
                    host text NOT NULL,
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

    def remove_active_user(self, username: str):
        c = self.conn.cursor()
        delete_statement = """DELETE FROM active_users
                              WHERE username = ? ;"""
        c.execute(delete_statement, (username,))

    def add_user_to_room(self, username: str, roomname: str):
        c = self.conn.cursor()
        update_statement = """UPDATE active_users
                              SET roomname = ?
                              WHERE username = ? ;"""
        c.execute(update_statement, (roomname, username))
        self.conn.commit()

    # TODO add user verification
    def create_room(self, username: str, roomname: str):
        """
        Create a new room assigned to a host (user that created room)
        :param username: username of host
        :param roomname: room name (visible to others)
        """
        room_schema = f"""CREATE TABLE IF NOT EXISTS {roomname} (
                    x INTEGER NOT NULL,
                    y INTEGER NOT NULL,
                    T INTEGER NOT NULL,
                    text_box text,
                    PRIMARY KEY (x, y)
                );
        """
        c = self.conn.cursor()
        c.execute(room_schema)
        table_values = f"""INSERT INTO {roomname} VALUES (?, ?, 3, NULL)"""
        for x in range(WINDOW_WIDTH):
            for y in range(WINDOW_HEIGHT):
                c.execute(table_values, (x, y))
        self.conn.commit()

        add_to_rooms_table = "INSERT INTO rooms(roomname, host) VALUES (?, ?)"
        c.execute(add_to_rooms_table, (roomname, username))
        self.conn.commit()

    def update_room_pixel(self, roomname: str, paint_message: bytes) -> None:
        c = self.conn.cursor()

        select_statement = """SELECT * FROM rooms WHERE roomname = ? ;"""
        c.execute(select_statement, (roomname,))
        rows = c.fetchall()
        if len(rows == 0):
            print(
                "WARNING: PAINT MESSAGE SENT TO ROOM THAT WAS NOT FOUND IN rooms TABLE"
            )
            return

        x = int.from_bytes(paint_message[:2], byteorder="big")
        y = int.from_bytes(paint_message[2:4], byteorder="big")
        T = paint_message[4]
        # T = 4 means CLEAR
        if T == 4:
            update_statement = f"""UPDATE {roomname}
                                   SET T = 3"""
            c.execute(update_statement)
        else:
            update_statement = f"""UPDATE {roomname}
                                   SET T = ?
                                   WHERE x = ? AND y = ? ;"""
            c.execute(update_statement, (T, x, y))
        self.conn.commit()

    def _get_room_pixel(self, roomname: str, x: int, y: int):
        c = self.conn.cursor()
        select_statement = f"""SELECT *
                               FROM {roomname}
                               WHERE x = ? AND y = ?"""
        c.execute(select_statement, (x, y))
        rows = c.fetchall()
        for row in rows:
            print(row)

    def _check_room(self, roomname: str):
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM {roomname}")

        rows = c.fetchall()

        for row in rows:
            print(row)
        print(f"Number of pixels: {len(rows)}")

    def host_disconnected(self, roomname: str):
        c = self.conn.cursor()
        update_statement = """UPDATE rooms
                              SET closed_at = ?
                              WHERE roomname = ?"""
        c.execute(update_statement, (datetime.datetime.now(), roomname))
        self.conn.commit()

    def room_timeout(self, roomname: str) -> bool:
        c = self.conn.cursor()
        select_statement = """SELECT closed_at
                              FROM rooms
                              WHERE roomname = ? ;"""
        c.execute(select_statement, (roomname,))
        vals = c.fetchall
        for val in vals:
            print(f"DEBUG STATEMENT: {val}")

        if len(vals) == 0:
            print("WARNING: ROOM NOT FOUND")
            return False

        # check if this works
        time: datetime.datetime = vals[0][0]

        if val is None:
            print(f"ROOM NOT CLOSED")
            return False

        time_passed: datetime.timedelta = datetime.datetime.now() - time
        SECONDS_IN_HOUR = 3600
        if time_passed.total_seconds() < SECONDS_IN_HOUR:
            print("ROOM NOT TIMED OUT")
            return False

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
        return True

        # TODO: send message to users to terminate their session

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
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        sql = """ INSERT INTO users(username, password, salt)
                  VALUES(?,?,?) """
        c = self.conn.cursor()
        c.execute(sql, (username, key, salt))
        self.conn.commit()
        return c.lastrowid

    def _select_all_users(self) -> None:
        """
        Query all rows in the users table
        :return:
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM users")

        rows = c.fetchall()

        for row in rows:
            print(row)

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
        db._select_all_users()
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