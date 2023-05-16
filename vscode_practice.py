
class User:
    username: str
    roomname: str
    is_host: bool = False

    def __init__(self, username: str, roomname: str):
        self.username = username
        self.roomname = roomname


def main():
    user = User("test", "test")
    user.roomname
    user.username = "test"
    print(f"{user.username=}, {user.roomname=}, {user.is_host=}")


if __name__ == "__main__":
    main()
