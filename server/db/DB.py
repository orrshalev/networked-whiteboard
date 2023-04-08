import sqlite3
import os
import hashlib
from sqlite3 import Error, Connection
import sys

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


# TODO: limit # of users that can be created
class DB:
    def __init__(self, db_file: str):
        """
        establish persistent connection
        """
        self.conn = sqlite3.connect(db_file)

    def _raw_command(self, sql: str) -> None:
        """Will execute any command given; do not use outside of file
        sql: SQLite query
        :return:
        """
        c = self.conn.cursor()
        c.execute(sql)

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
                    text_box text
                );
        """
        c = self.conn.cursor()
        c.execute(room_schema)
        table_values = f"""INSERT INTO {roomname} VALUES (?, ?, 3, NULL)"""
        for x in range(WINDOW_WIDTH):
            for y in range(WINDOW_HEIGHT):
                c.execute(table_values, (x, y))
        self.conn.commit()

    def _check_room(self, roomname: str):
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM {roomname}")

        rows = c.fetchall()

        for row in rows:
            print(row)
        print(f"Number of pixels: {len(rows)}")

    def close_room(self, roomname: str):
        """
        Drops table with roomname
        :param roomname:
        """
        drop_room = f"""DROP TABLE IF EXISTS {roomname} ; """
        c = self.conn.cursor()
        c.execute(drop_room)

    def create_user(self, username: str, password: str) -> int:
        """
        Create a new user into the users table
        :param user[0]: username
        :param user[1]: non-hashed password
        :return: user id
        """
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        sql = """ INSERT INTO users(username, password,salt)
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

    else:
        explainer = """
            RUN FROM db DIRECTORY

            python ./DB.py CREATE_USER_TABLE
            python ./DB.py ADD_USER <username> <password>
            python ./DB.py SELECT_ALL_USERS
        """
        raise Exception(explainer)

    db.close_connection()


if __name__ == "__main__":
    main()
