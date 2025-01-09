import os
import platform

from twisted.web import server
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP6ServerEndpoint 

import requests

class Handler(Resource):
    isLeaf = True

    def render_GET(self, request):
                
        bodytext = "Hello!\nThis Python application supports IPv4 as well as IPv6\n"   
        
        match platform.system:
            case "Linux":
                bodytext += "running on Linux\n"
                fd = open('/proc/sys/net/ipv6/bindv6only', r)
                bindv6only = read(fd)
                close(fd)
                if bindv6only:
                    bodytext += "IPv6 Wildcard sockets also bind on IPv4 by default - that does not help you in python\n"
                else:
                    bodytext += "IPv6 Wildcard sockets do not bind on IPv4 by default)\n"

        try:
            rd = requests.get('http://ds.test-ipv6.com/ip/',   params={'callback': 'ds'},  timeout=0.20)
            bodytext += "callout-{}\n".format(rd.text.rstrip())
        except requests.exceptions.RequestException as e:
            bodytext += "callout-ds({})\n".format(e)                
        try:
            r4 = requests.get('http://ipv4.test-ipv6.com/ip/', params={'callback': 'ip4'}, timeout=0.20)
            bodytext += "callout-{}\n".format(r4.text.rstrip())
        except requests.exceptions.RequestException as e:
            bodytext += "callout-ip4({})\n".format(e)

        try: 
            r6 = requests.get('http://ipv6.test-ipv6.com/ip/', params={'callback': 'ip6'}, timeout=0.20)
            bodytext += "callout-{}\n".format(r6.text.rstrip())
        except requests.exceptions.RequestException as e:
            bodytext += "callout-"+"ip6({})\n".format(e)

        return(bodytext.encode('utf-8'))


site = server.Site(Handler())
endpoint4 = TCP4ServerEndpoint(reactor, int(os.getenv('PORT')))
endpoint4.listen(site)
endpoint6 = TCP6ServerEndpoint(reactor, int(os.getenv('PORT')))
endpoint6.listen(site)
reactor.run()
