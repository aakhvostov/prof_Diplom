from server import Server


group_token = input('Token: ')


if __name__ == '__main__':
    Server(group_token).start()
