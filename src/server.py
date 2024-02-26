#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
# @project HTTP resolver domenovych mien - IPK2020
#
# @file server.py
# @brief Server pre preklad domenovych mien.
#
# @author Roman Fulla <xfulla00>
# @date 25.03.2020
################################################################################

import signal
import socket
import sys

BUFFER = 1024                                                                   # Velkost buffera


'''
OPRAVY po termine:
    Pridane zahodenie nepodstatnych informacii
    Odstranenie problemovej kontroly HTTP/
    Oprava chybovych sprav na spravny format (HTTP/1.1 ERROR cislo na HTTP/1.1 cislo)
    Oprava POST pri chybnom formate poziadavku - pochopene, ze ak ma nejaky poziadavok nespravny format, cely request je zly
    Pridana podpora prazdneho POST
    Pridana podpora CRLF
    .close() presunuty z finally do except
'''


def eprint(*args, **kwargs):                                                    # Vypis na stderr
    print(*args, file=sys.stderr, **kwargs)


def handle_GET(argument):                                                       # Spracovanie operacie GET
    argument = argument.split('\r\n')[0]                                        # Zahodenie nepodstatnych informacii

    argument = argument.split("=")                                              # Rozdelenie poziadavku
    if len(argument) != 3:                                                      # Neocakavany pocet po rozdeleni
        return "HTTP/1.1 400 Bad Request.\r\n\r\n"
    if argument[0] != '/resolve?name':                                          # Vstup nesplna ocakavany format
        return "HTTP/1.1 400 Bad Request.\r\n\r\n"
    if (argument[1])[-5:] != '&type':                                           # Vstup nesplna ocakavany format
        return "HTTP/1.1 400 Bad Request.\r\n\r\n"

    name = ((argument[1])[:-5]).strip()                                         # Domenove meno alebo IP adresa
    r_type = ((argument[2])[:-9]).strip()                                       # Typ pozadovanej odpovedi

    try:
        if r_type == 'A':
            if name == socket.gethostbyname(name):                              # Dostali sme IP miesto domenoveho mena
                return "HTTP/1.1 400 Bad Request.\r\n\r\n"
            result = socket.gethostbyname(name)                                 # Vysledna odpoved
        elif r_type == 'PTR':
            if name != socket.gethostbyname(name):                              # Dostali sme domenove meno miesto IP
                return "HTTP/1.1 400 Bad Request.\r\n\r\n"
            result = socket.gethostbyaddr(name)[0]                              # Vysledna odpoved
        else:                                                                   # Nepodporovany typ pozadovanej odpovedi
            return "HTTP/1.1 400 Bad Request.\r\n\r\n"
    except OSError:                                                             # Odpoved nebola najdena
        return "HTTP/1.1 404 Not Found\r\n\r\n"

    result = name + ':' + r_type + '=' + result                                 # OTAZKA:TYP=ODPOVED
    return "HTTP/1.1 200 OK\r\n\r\n" + result                                   # Vratenie vysledku


def handle_POST(argument):                                                      # Spracovanie operacie POST
    argument = argument.split("\r\n\r\n")                                       # Rozdelenie spravy na hlavicku a poziadavky
    if len(argument) > 2:                                                       # Neocakavany pocet po rozdeleni
        return "HTTP/1.1 400 Bad Request.\r\n\r\n"

    header = argument[0].split('\r\n')[0]                                       # Zahodenie nepodstatnych informacii
    if (header[:-9] != '/dns-query'):                                           # Hlavicka nesplna ocakavany format
        return "HTTP/1.1 400 Bad Request.\r\n\r\n"

    if len(argument) == 1:                                                      # Prazdny POST
        return "HTTP/1.1 200 OK\r\n\r\n"

    requests = argument[1]                                                      # Poziadavky
    requests = requests.replace("\r", '')                                       # Podpora CRLF

    try:
        result = ''                                                             # Vysledna odpoved
        for request in requests.splitlines():                                   # Spracovavanie poziadaviek
            try:
                (name, r_type) = request.split(":", 1)                          # Domenove meno alebo IP adresa & Typ pozadovanej odpovedi
            except ValueError:                                                  # Vstup nesplna ocakavany format
                continue

            name = name.strip()                                                 # Zbavenie sa medzier
            r_type = r_type.strip()                                             # Zbavenie sa medzier

            try:
                if r_type == 'A':
                    if name == socket.gethostbyname(name):                      # Dostali sme IP miesto domenoveho mena
                        continue
                    entry = socket.gethostbyname(name)                          # Odpoved pre poziadavku
                elif r_type == 'PTR':
                    if name != socket.gethostbyname(name):                      # Dostali sme domenove meno miesto IP
                        continue
                    entry = socket.gethostbyaddr(name)[0]                       # Odpoved pre poziadavku
                else:                                                           # Nepodporovany typ pozadovanej odpovedi
                    continue
            except OSError:                                                     # Odpoved nebola najdena
                continue

            result = result + "\n" + name + ':' + r_type + '=' + entry          # OTAZKA:TYP=ODPOVED
    except ValueError:                                                          # Vstup nesplna ocakavany format
        return "HTTP/1.1 400 Bad Request.\r\n\r\n"

    if result == '':                                                            # Ani jedna poziadavka nebola spravne podana
        return "HTTP/1.1 400 Bad Request.\r\n\r\n"

    return "HTTP/1.1 200 OK\r\n\r\n" + result                                   # Vratenie vysledku


"""___MAIN___"""                                                                # Hlavny program
if len(sys.argv) != 2:
    eprint('Nespravny pocet parametrov.')
    sys.exit(1)

port = (sys.argv[1])                                                            # Ziskanie portu
if not port.isdigit():
    eprint('Nespravne zadany parameter.')
    sys.exit(2)
if not (1024 <= int(port) < 65536):
    eprint('Nevhodna identifikacia portu.')
    sys.exit(3)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)               # Vytvorenie socketu
server_socket.bind(("", int(port)))
server_socket.listen()

try:
    while True:                                                                 # Fungovanie servera
        client_socket, adress = server_socket.accept()

        msg = ''                                                                # Sprava od klienta
        client_socket.settimeout(0.5)
        while True:                                                             # Ziskavanie spravy od klienta
            try:
                msg_part = client_socket.recv(BUFFER)
            except socket.timeout:                                              # Podmienka pre ukoncenie cyklu
                break
            msg = msg + msg_part.decode('utf-8')

        msg = msg.strip()                                                       # Zbavenie sa medzier
        (operation, argument) = msg.split(" ", 1)                               # Rozdelenie spravy na operaciu a poziadavky
        if operation == 'GET':                                                  # Spracovanie operacie GET
            result = handle_GET(argument).encode('utf-8')
        elif operation == 'POST':                                               # Spracovanie operacie POST
            result = handle_POST(argument).encode('utf-8')
        else:                                                                   # Nepodporovana operacia
            result = ("HTTP/1.1 405 Method Not Allowed.\r\n\r\n").encode('utf-8')

        client_socket.sendall(result)                                           # Odoslanie odpovede
        client_socket.close()
except KeyboardInterrupt:                                                       # Uzivatelom vyziadane vypnutie servera (CTRL + C)
    server_socket.close()                                                       # Upratanie
    sys.exit(0)
