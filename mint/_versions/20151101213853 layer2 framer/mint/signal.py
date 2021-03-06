import mint

class Signal(object):

    def __init__(self):
        self.slots = []
        self.event = mint.env.event()

    def connect(self, slot):
        self.slots.append(slot)

    def __call__(self, *args, **kwargs):
        for slot in self.slots:
            slot(*args, **kwargs)
        self.event.succeed()
        self.event = mint.env.event()

if __name__ == '__main__':
    def f(a, b, name='what'):
        print a, b, name
    def g(*args, **kwargs):
        print 'g', args
    s = Signal()
    s.connect(f)
    s.connect(g)
    s(1, 2, name='foo')
