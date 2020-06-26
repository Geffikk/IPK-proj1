#!/usr/bin/env python

import socket
import re
import sys

TCP_IP = '127.0.0.1'
#TCP_PORT = 5545
TCP_PORT = int(sys.argv[1])
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

if TCP_PORT > 68235:
    sys.exit("HTTP/1.1 500 Internal server error" + "\r\n\r\n" + "\n")


def get_function(data):

    addrInfo = ""
    infos = data[1]

    # Resolver, URL, Type
    resolve_url_type = infos.split('=', 1)
    resolve_part_fin = resolve_url_type[0]

    # URL, Type
    url_type = resolve_url_type[1].split('&', 1)

    if resolve_part_fin != '/resolve?name' or len(url_type) != 2:
        response = "HTTP/1.1 400 Bad Request" + "\r\n\r\n"
        conn.sendall(response.encode())
        return

    # Domena
    url_part_fin = url_type[0]

    # Type = A/PTR
    type_type = url_type[1].split('=', 1)
    type_str = type_type[0]
    type_part_fin = type_type[1]

    if type_str != 'type':
        response = "HTTP/1.1 400 Bad Request" + "\r\n\r\n"
        conn.sendall(response.encode())
        return

    bad_request = False
    not_found = False
    if type_part_fin == 'A':
        if re.match("[www]*[.]*[\w]*[.]*[\w]*[.]*[\w]+[.][a-zA-Z]+$", url_part_fin) is None:
            bad_request = True
        try:
            addrInfo = socket.gethostbyname(url_part_fin)
        except socket.gaierror:
            not_found = True

        if not_found == False and bad_request == False:
            response = "HTTP/1.1 200 OK" + "\r\n\r\n" + url_part_fin + ":" + type_part_fin + "=" + addrInfo + "\n"
        elif bad_request == True:
            response = "HTTP/1.1 400 Bad Request" + "\r\n\r\n"
        else:
            response = "HTTP/1.1 404 Not Found" + "\r\n\r\n"

        conn.sendall(response.encode())

    elif type_part_fin == 'PTR':
        if re.match("(?:^|\b(?<!\.))(?:1?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:1?\d\d?|2[0-4]\d|25[0-5])){3}(?=$|[^\w.])", url_part_fin) is None:
            bad_request = True
        try:
            addrInfo = socket.gethostbyaddr(url_part_fin)
        except socket.herror:
            not_found = True

        if not_found == False and bad_request == False:
            response = "HTTP/1.1 200 OK" + "\r\n\r\n" + url_part_fin + ":" + type_part_fin + "=" + addrInfo[0] + "\n"
        elif bad_request == True:
            response = "HTTP/1.1 400 Bad Request" + "\r\n\r\n"
        else:
            response = "HTTP/1.1 404 Not Found" + "\r\n\r\n"

        conn.sendall(response.encode())

    else:
        response = "HTTP/1.1 400 Bad Request" + "\r\n\r\n"
        conn.sendall(response.encode())

    return

def post_function(data, ws_data):

    i = 0
    dns_query = data[1]

    files_data = ws_data.split('\r\n')
    files_data = files_data[7].split('\n')

    header = "HTTP/1.1 200 OK" + "\r\n\r\n"
    response = ""

    if files_data[0] == "" and len(files_data) == 1:
        header = "HTTP/1.1 400 Bad Request" + "\r\n\r\n"
        conn.sendall(header.encode())
        return

    if files_data[-1] == "":
        files_data.pop(-1)

    if files_data[-1] == "":
        files_data.pop(-1)

    if files_data[-1] == "":
        header = "HTTP/1.1 400 Bad Request" + "\r\n\r\n"
        conn.sendall(header.encode())
        return


    if dns_query != '/dns-query':
        response = "HTTP/1.1 400 Bad Request" + "\r\n\r\n"
        conn.sendall(response.encode())
        return

    not_found = True
    bad_request = False

    while (i != len(files_data)):

        domain = files_data[i].split(':')
        if len(domain) != 2:
            bad_request = True
            i = i + 1
            continue
        try:
            type = domain[1]
        except:
            bad_request = True
            i = i + 1
            continue

        if type == 'A':

            if re.match("[www]*[.]*[\w]*[.]*[\w]*[.]*[\w]+[.][a-zA-Z]+$", domain[0]) is None:
                bad_request = True
                i = i + 1
                continue

            try:
                addrInfo = socket.gethostbyname(domain[0])
                not_found = False
            except socket.gaierror:
                i = i + 1
                continue

            response = response + domain[0] + ":" + domain[1] + "=" + addrInfo + "\n"


        elif type == 'PTR':

            if re.match("(?:^|\b(?<!\.))(?:1?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:1?\d\d?|2[0-4]\d|25[0-5])){3}(?=$|[^\w.])", domain[0]) is None:
                #bad_request = True
                i = i + 1
                continue

            try:
                addrInfo = socket.gethostbyaddr(domain[0])
                not_found = False
            except socket.herror:
                i = i + 1
                continue

            response = response + domain[0] + ":" + domain[1] + "=" + addrInfo[0] + "\n"

        else:
            bad_request = True

        i = i + 1

    if bad_request == True and not_found == True: header = "HTTP/1.1 400 Bad Request" + "\r\n\r\n"
    if not_found == True and bad_request == False: header = "HTTP/1.1 404 Not Found" + "\r\n\r\n"
    final_response = header + response
    conn.sendall(final_response.encode())
    return

while 1:
    conn, addr = s.accept()
    curl_data = conn.recv(BUFFER_SIZE).decode()

    if not curl_data:
        final_ret = "HTTP/1.1 500 Internal server error" + "\r\n\r\n" + "\n"
        conn.sendall(final_ret.encode())

    get_data = curl_data.split()
    post_data = curl_data.replace(" ", "")

    get_or_post = get_data[0]

    if get_or_post == 'GET':
        get_function(get_data)
    elif get_or_post == 'POST':
        post_function(get_data, post_data)
    else:
        response = "HTTP/1.1 405 Method Not Allowed" + "\r\n\r\n"
        conn.sendall(response.encode())

    conn.close()



