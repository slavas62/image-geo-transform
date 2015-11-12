from twisted.web.client import ResponseDone, PotentialDataLoss, PartialDownloadError
from twisted.internet import reactor, protocol, defer
from twisted.internet.defer import inlineCallbacks

class FileWriterProtocol(protocol.Protocol):
    def __init__(self, fp, status, message, deferred):
        self.deferred = deferred
        self.status = status
        self.message = message
        self.fp = fp

    def _write(self, data):
        self.fp.write(data)
        self.fp.flush()

    def _flush(self):
        self.fp.flush()

    def dataReceived(self, data):
        reactor.callInThread(self._write, data)
        
    @inlineCallbacks
    def connectionLost(self, reason):
        if reason.check(ResponseDone):
            yield reactor.callInThread(self._flush)
            self.deferred.callback(None)
        elif reason.check(PotentialDataLoss):
            self.deferred.errback(
                PartialDownloadError(self.status, self.message))
        else:
            self.deferred.errback(reason)

def write_body_to_file(response, fp):
    def cancel(deferred):
        abort = getAbort()
        if abort is not None:
            abort()

    d = defer.Deferred(cancel)
    protocol = FileWriterProtocol(fp, response.code, response.phrase, d)
    
    def getAbort():
        return getattr(protocol.transport, 'abortConnection', None)

    response.deliverBody(protocol)
    return d
