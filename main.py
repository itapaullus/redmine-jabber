# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


from twisted.internet import reactor, protocol
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineOnlyReceiver

class Echo(LineOnlyReceiver):
    """This is just about the simplest possible protocol"""
    name = ""

    def getName(self):
        if self.name != "":
            return self.name.decode('utf-8')
        return self.transport.getPeer().host

    # def dataReceived(self, data):
    #     "As soon as any data is received, write it back."
    #     # print(type(data))
    #     # print(data)
    #     self.transport.write(data)

    def connectionMade(self):
        print ("New connection from "+'self.getName()')
        self.sendLine("Welcome to my my chat server.")
        self.sendLine("Send '/NAME [new name]' to change your name.")
        self.sendLine("Send '/EXIT' to quit.")
        print(type(self.getName()))
        message = str(self.getName()) + ' has joined the party.'
        self.factory.sendMessageToAllClients(message.encode('utf-8'))
        self.sendLine(message)
        self.factory.clientProtocols.append(self)

    def connectionLost(self, reason):
        print("Lost connection from " + self.getName())
        self.factory.clientProtocols.remove(self)
        self.factory.sendMessageToAllClients(str(self.getName()+" has disconnected").encode('utf-8'))

    def lineReceived(self, line):
        # print(self.getName() + " said ".encode('utf-8') + line)
        if line[:5] == b"/NAME":
            oldName = self.getName()
            self.name = line[5:].strip()
            message = str(oldName) + " changed name to " + self.getName().decode('utf-8')
            self.factory.sendMessageToAllClients(message.encode('utf-8'))
        elif line == b"/EXIT":
            self.transport.loseConnection()
        else:
            message = self.getName() + " says " + line.decode('utf8')
            self.factory.sendMessageToAllClients(message.encode('utf-8'))

    def sendLine(self, line: str):
        if isinstance(line, str):
            self.transport.write(str(line + '\r\n').encode('utf-8'))
        else:
            self.transport.write(line)
            self.sendLine('\r\n')


class ChatProtocolFactory(ServerFactory):
    protocol = Echo
    def __init__(self):
        self.clientProtocols = []
    def sendMessageToAllClients(self, mesg):
        for client in self.clientProtocols:
            client.sendLine(mesg)


def main():
    """This runs the protocol on port 8000"""
    factory = ChatProtocolFactory()
    factory.protocol = Echo
    reactor.listenTCP(8000, factory)
    reactor.run()


# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
