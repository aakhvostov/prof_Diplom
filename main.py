from server import Server


VK_GROUP_TOKEN = input('VK_GROUP_Token: ')


if __name__ == '__main__':
    Server(VK_GROUP_TOKEN).start()
    