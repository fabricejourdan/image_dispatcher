class Pager(object):
    def __init__(self, count):
        self.count = count
        self.current = 0

    @property
    def first(self):
        return 0

    @property
    def next(self):
        n = self.current
        if n < self.count - 1:
            n += 1
        return n
        
    @property
    def prev(self):
        n = self.current
        if n > 0:
            n -= 1
        return n
        
    @property
    def last(self):
        return self.count - 1