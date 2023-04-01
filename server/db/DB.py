import sqlite3
from sqlite3 import Error, Connection
import sys


# TODO: limit # of users that can be created
class DB:

    
    def __init__(self, db_file: str):
        """
        establish persistent connection
        """
        self.conn = sqlite3.connect(db_file)

    def create_table(self, create_table_sql: str) -> None:
        """create a table from the create_table_sql statement
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_user(self, user: tuple[str, str]) -> int:
        """
        Create a new user into the users table
        :param user:
        :return: user id
        """
        sql = """ INSERT INTO users(username, password)
                  VALUES(?,?) """
        cur = self.conn.cursor()
        cur.execute(sql, user)
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

    def check_user_credentials(self, username: str, hashedPassword: str) -> bool:
        """
        Check if user credentials are correct
        """
        cur = self.conn.cursor()
        cur.execute(""" SELECT *
                        FROM users
                        WHERE username=? 
                        AND password=?""", (username, hashedPassword))
        
        rows = cur.fetchall()

        if len(rows) > 0:
            return True
        return False

    def close_connection(self):
        """
        Needs to be done when program exits if DB was initialized
        """
        self.conn.close();

def main():
    database = "./app.db"
    db = DB(database)

    if len(sys.argv) == 2 and sys.argv[1] == "CREATE_USER_TABLE":
        user_schema = """CREATE TABLE IF NOT EXISTS users (
                    id integer PRIMARY KEY,
                    username text NOT NULL,
                    password text NOT NULL
                ); """
        db.create_table(user_schema)
    elif (
        len(sys.argv) == 4 and sys.argv[1] == "ADD_USER"
    ):  # arg count of 4 based on adding username and password only
        user = (sys.argv[2], sys.argv[3])
        user_id = db.create_user(
             user
        )  # user_id can be used for relational purposes
    elif len(sys.argv) == 2 and sys.argv[1] == "SELECT_ALL_USERS":
        db.select_all_users()
    elif len(sys.argv) == 4 and sys.argv[1] == "CHECK_USER":
        user_exists = db.check_user_credentials(sys.argv[2], sys.argv[3])
        if (user_exists):
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
