# Prints the position of the cursor and then the line, for each line in the file


def test():
    with open("good_mourning.txt", "r") as greetings:
        while True:
                print(greetings.tell())
                print(greetings.readline())
