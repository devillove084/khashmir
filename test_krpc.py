from unittest import *
from krpc import *
from airhook import *

import sys

if __name__ =="__main__":
    tests = unittest.defaultTestLoader.loadTestsFromNames([sys.argv[0][:-3]])
    result = unittest.TextTestRunner().run(tests)


def connectionForAddr(host, port):
    return host
    
class Receiver(protocol.Factory):
    protocol = KRPC
    def __init__(self):
        self.buf = []
    def krpc_store(self, msg, _krpc_sender):
        self.buf += [msg]
    def krpc_echo(self, msg, _krpc_sender):
        return msg

class SimpleTest(TestCase):
    def setUp(self):
        self.noisy = 0
        
        self.af = Receiver()
        self.bf = Receiver()        
        self.a = listenAirhookStream(4040, self.af)
        self.b = listenAirhookStream(4041, self.bf)
        
    def testSimpleMessage(self):
        self.noisy = 1
        self.a.connectionForAddr(('127.0.0.1', 4041)).protocol.sendRequest('store', {'msg' : "This is a test."})
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        self.assertEqual(self.bf.buf, ["This is a test."])

class SimpleTest(TestCase):
    def setUp(self):
        self.noisy = 0
        
        self.af = Receiver()
        self.bf = Receiver()        
        self.a = listenAirhookStream(4050, self.af)
        self.b = listenAirhookStream(4051, self.bf)
        
    def testSimpleMessage(self):
        self.noisy = 1
        self.a.connectionForAddr(('127.0.0.1', 4051)).protocol.sendRequest('store', {'msg' : "This is a test."})
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        self.assertEqual(self.bf.buf, ["This is a test."])

class EchoTest(TestCase):
    def setUp(self):
        self.noisy = 0
        self.msg = None
        
        self.af = Receiver()
        self.bf = Receiver()        
        self.a = listenAirhookStream(4042, self.af)
        self.b = listenAirhookStream(4043, self.bf)
        
    def testEcho(self):
        self.noisy = 1
        df = self.a.connectionForAddr(('127.0.0.1', 4043)).protocol.sendRequest('echo', {'msg' : "This is a test."})
        df.addCallback(self.gotMsg)
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        self.assertEqual(self.msg, "This is a test.")

    def gotMsg(self, msg):
        self.msg = msg

class MultiEchoTest(TestCase):
    def setUp(self):
        self.noisy = 0
        self.msg = None
        
        self.af = Receiver()
        self.bf = Receiver()        
        self.a = listenAirhookStream(4048, self.af)
        self.b = listenAirhookStream(4049, self.bf)
        
    def testMultiEcho(self):
        self.noisy = 1
        df = self.a.connectionForAddr(('127.0.0.1', 4049)).protocol.sendRequest('echo', {'msg' : "This is a test."})
        df.addCallback(self.gotMsg)
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        self.assertEqual(self.msg, "This is a test.")

        df = self.a.connectionForAddr(('127.0.0.1', 4049)).protocol.sendRequest('echo', {'msg' : "This is another test."})
        df.addCallback(self.gotMsg)
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        self.assertEqual(self.msg, "This is another test.")

        df = self.a.connectionForAddr(('127.0.0.1', 4049)).protocol.sendRequest('echo', {'msg' : "This is yet another test."})
        df.addCallback(self.gotMsg)
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        self.assertEqual(self.msg, "This is yet another test.")

    def gotMsg(self, msg):
        self.msg = msg

class UnknownMethErrTest(TestCase):
    def setUp(self):
        self.noisy = 0
        self.err = None
        self.af = Receiver()
        self.bf = Receiver()        
        self.a = listenAirhookStream(4044, self.af)
        self.b = listenAirhookStream(4045, self.bf)
        
    def testUnknownMeth(self):
        self.noisy = 1
        df = self.a.connectionForAddr(('127.0.0.1', 4045)).protocol.sendRequest('blahblah', {'msg' : "This is a test."})
        df.addErrback(self.gotErr)
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        reactor.iterate()
        self.assertEqual(self.err, KRPC_ERROR_METHOD_UNKNOWN)

    def gotErr(self, err):
        self.err = err.value
