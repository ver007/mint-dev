from mint.components import Endpoint

class PC(Endpoint):

    def __init__(self, name=None):
        super(PC, self).__init__(name)

    def send(self, data):
        self.port.send(data)

    def recv(self, nbits):
        data = ''
        for _ in range(nbits):
            data += self.port.recv(1)
        return data