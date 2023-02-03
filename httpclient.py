#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return "Code: 200" + '\nBody: \n' + self.body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = int(data.split(' ')[1])
        return code if code else 400

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data.split('\r\n\r\n')[1] if len(data.split('\r\n\r\n')) > 1 else ''

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def populate_info(self, url):
        urlInfo = {}
        parsedUrl = urllib.parse.urlparse(url)
        urlInfo["path"] = parsedUrl.path if parsedUrl.path else "/"
        urlInfo["hostname"] = parsedUrl.hostname if parsedUrl.hostname else "/"
        urlInfo["port"] = parsedUrl.port if parsedUrl.port else 80

        return urlInfo

    def GET(self, url, args=None):
        urlInfo = self.populate_info(url)
        self.connect(urlInfo["hostname"], urlInfo["port"])
        self.sendall(
            f'GET {urlInfo["path"]} HTTP/1.0\r\nHost: {urlInfo["hostname"]}:{urlInfo["port"]}\r\nConnection: Close\r\n\r\n'
        )
        data = self.recvall(self.socket)
        self.close()

        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        urlInfo = self.populate_info(url)
        self.connect(urlInfo["hostname"], urlInfo["port"])
        baseRequest = f'POST {urlInfo["path"]} HTTP/1.0\r\nHost: {urlInfo["hostname"]}:{urlInfo["port"]}\r\nConnection: Close\r\n'

        if args == None:
            self.sendall(
                baseRequest + 'Content-Length: 0\r\n\r\n'
            )
        else:
            queryParameters = ""

            for key in args:
                value = args[key]
                queryParameters += key + "=" + value + "&"
            queryParameters = queryParameters[:-1]
            self.sendall(
                baseRequest + 'Content-Type: application/x-www-form-urlencoded\r\nContent-Length: ' 
                + str(len(queryParameters.encode("utf-8"))) + '\r\n\r\n' + queryParameters + '\r\n\r\n'
            )
        data = self.recvall(self.socket)
        self.close()

        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
