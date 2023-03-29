import sqlite3
from sqlite3 import Error, Connection
import sys


class DB:
    def create_connection(db_file: str) -> Connection:
        """create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = sqlite3.connect(db_file)
        return conn

    def create_table(conn: Connection, create_table_sql: str) -> None:
        """create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_user(conn: Connection, user: tuple[str, str]) -> int:
        """
        Create a new user into the users table
        :param conn:
        :param user:
        :return: user id
        """
        sql = """ INSERT INTO users(username, password)
                  VALUES(?,?) """
        cur = conn.cursor()
        cur.execute(sql, user)
        conn.commit()
        return cur.lastrowid

    def select_all_users(conn: Connection) -> None:
        """
        Query all rows in the users table
        :param conn:
        :return:
        """
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")

        rows = cur.fetchall()

        for row in rows:
            print(row)


def main():
    database = "./app.db"
    conn = DB.create_connection(database)

    if len(sys.argv) == 2 and sys.argv[1] == "CREATE_USER_TABLE":
        user_schema = """CREATE TABLE IF NOT EXISTS users (
                    id integer PRIMARY KEY,
                    username text NOT NULL,
                    password text NOT NULL
                ); """
        DB.create_table(conn, user_schema)
    elif (
        len(sys.argv) == 4 and sys.argv[1] == "ADD_USER"
    ):  # arg count of 4 based on adding username and password only
        with conn:
            user = (sys.argv[2], sys.argv[3])
            user_id = DB.create_user(
                conn, user
            )  # user_id can be used for relational purposes
    elif len(sys.argv) == 2 and sys.argv[1] == "SELECT_ALL_USERS":
        with conn:
            DB.select_all_users(conn)
    else:
        explainer = """
            RUN FROM db DIRECTORY

            python ./DB.py CREATE_USER_TABLE
            python ./DB.py ADD_USER <username> <password>
        """
        raise Exception(explainer)


if __name__ == "__main__":
    main()
