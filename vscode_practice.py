class User:
    username: str
    roomname: str
    is_host: bool = False

    def __init__(self, username: str, roomname: str):
        self.username = username
        self.roomname = roomname


def loop():
    my_bool = True
    while my_bool:
        print("looping")


def main():
    user = User("test", "test")
    username = "test"
    user.roomname
    user.username = "est"
    user.username
    username = "nottest"
    # print(f"{user.username=},  {user.roomname=}, {user.is_host=}")


if __name__ == "__main__":
    main()
