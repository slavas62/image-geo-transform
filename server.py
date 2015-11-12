import sys

from twisted.web import server
from twisted.internet import reactor, endpoints
from twisted.python import usage
from resources import MainResource

class Options(usage.Options):

    optFlags = [
    ]
    optParameters = [
        ['port', 'p', '8000', "Server port"],
        ['save-dir', 'd', '/tmp/', "Directory for saving result images"],
        ['save-dir-url', 'u', '/files/', "Uri prefix for saved images"],
    ]

def main():
    config = Options()
    try:
        config.parseOptions() # When given no argument, parses sys.argv[1:]
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
    
    print 'save result images to: %s' % config['save-dir']    
    print 'listening on: %s' % config['port']
    
    kwargs = dict(save_dir=config['save-dir'], save_dir_url=config['save-dir-url'])
    endpoints.serverFromString(reactor, 'tcp:%s' % config['port']).listen(server.Site(MainResource(**kwargs)))
    reactor.run()

if __name__ == "__main__":
    main()
