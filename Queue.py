

class Queue:
    """
    Very Simple and inefficient queue
    """
    def __init__(self):
        self.lst = []

    def put(self, data):
        self.lst.insert(0, data)

    def get(self):
        return self.lst.pop()

    def show(self):
        return self.lst[-1]

    def empty(self):
        return not self.lst
