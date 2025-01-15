def input_user():
    print("\x1b[6;30;43m" + "user(q to quit) : " + "\x1b[0m", end="")
    return input()


def print_agent(message, end="\n"):
    print("\x1b[6;30;43m" + "agent: " + "\x1b[0m" + message, end=end)


def print_system(message, end="\n"):
    print("\x1b[6;30;44m" + "system: " + "\x1b[0m" + message, end=end)
