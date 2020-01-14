def test():
    with open("good_mourning.txt", "r") as greetings:
        while True:
                print(greetings.tell())
                print(greetings.readline())
