import socket
import os
import platform

import h2.connection
import h2.config

import requests

# Example H2C web app
# Based on https://python-hyper.org/projects/h2/en/stable/basic-usage.html#writing-your-server


def handle(sock):
    config = h2.config.H2Configuration(client_side=False)
    conn = h2.connection.H2Connection(config=config)
    conn.initiate_connection()
    sock.sendall(conn.data_to_send())

    while True:
        data = sock.recv(65535)
        if not data:
            break

        events = conn.receive_data(data)
        for event in events:
            if isinstance(event, h2.events.RequestReceived):
                bodytext = "Hello!\nThis Python application is speaking plain text HTTP2 (H2C) with the CF routing layer and supports IPv4 as well as IPv6\n"

                match platform.system:
                    case "Linux":
                        bodytext += "running on Linux\n"
                        fd = open('/proc/sys/net/ipv6/bindv6only', r)
                        bindv6only = read(fd)
                        close(fd)
                        if bindv6only:
                            bodytext += "IPv6 Wildcard sockets also bind on IPv4 by default\n"
                        else:
                            bodytext += "IPv6 Wildcard sockets do not bind on IPv4 by default - needs sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)\n"
                    
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

                stream_id = event.stream_id
                conn.send_headers(
                    stream_id=stream_id,
                    headers=[
                        (':status', '200'),
                        ('content-type', 'text/plain')
                    ],
                )
                conn.send_data(
                    stream_id=stream_id,
                    data=bodytext.encode(),
                    end_stream=True
                )

        data_to_send = conn.data_to_send()
        if data_to_send:
            sock.sendall(data_to_send)

sock = socket.socket(family=socket.AF_INET6)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('::', int(os.getenv('PORT'))))
sock.listen(5)

while True:
    handle(sock.accept()[0])
