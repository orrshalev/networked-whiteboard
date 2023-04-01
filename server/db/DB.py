import sqlite3
import os
import hashlib
from sqlite3 import Error, Connection
import sys


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
        cur = self.conn.cursor()
        cur.execute(sql, (username, key, salt))
        self.conn.commit()
        return cur.lastrowid

    def select_all_users(self) -> None:
        """
        Query all rows in the users table
        :return:
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users")

        rows = cur.fetchall()

        for row in rows:
            print(row)

    def check_user_credentials(self, username: str, password: str) -> bool:
        """
        Check if user credentials match a value in users table
        """
        cur = self.conn.cursor()
        cur.execute(
            """ SELECT *
                        FROM users
                        WHERE username=?""",
            (username,),
        )

        rows = cur.fetchall()

        if len(rows) > 0:
            user = rows[0]
            key = user[2]
            salt = user[3]
            new_key = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, 100000
            )
            if key == new_key:
                return True

        return False

    def close_connection(self):
        """
        Needs to be done when program exits if DB was initialized
        """
        self.conn.close()


def main():
    database = "./app.db"
    db = DB(database)

    if len(sys.argv) == 2 and sys.argv[1] == "CREATE_USER_TABLE":
        user_schema = """CREATE TABLE IF NOT EXISTS users (
                    id integer PRIMARY KEY,
                    username text NOT NULL,
                    password text NOT NULL,
                    salt     text NOT NULL
                ); """
        db._raw_command(user_schema)
    elif len(sys.argv) == 2 and sys.argv[1] == "DELETE_USER_TABLE":
        delete_user_table = """DROP TABLE IF EXISTS users;"""
        db._raw_command(delete_user_table)
    elif (
        len(sys.argv) == 4 and sys.argv[1] == "ADD_USER"
    ):  # arg count of 4 based on adding username and password only
        user_id = db.create_user(sys.argv[2], sys.argv[3])  # user_id can be used for relational purposes
    elif len(sys.argv) == 2 and sys.argv[1] == "SELECT_ALL_USERS":
        db.select_all_users()
    elif len(sys.argv) == 4 and sys.argv[1] == "CHECK_USER":
        user_exists = db.check_user_credentials(sys.argv[2], sys.argv[3])
        if user_exists:
            print(f"User with credentials {sys.argv[2]} {sys.argv[3]} in table")
        else:
            print(f"User with credentials {sys.argv[2]} {sys.argv[3]} not found")
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
