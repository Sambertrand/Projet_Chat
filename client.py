#!/usr/bin/env python3
# chat.py
# author: Sebastien Combefis
# version: February 15, 2016

import socket
import sys
import threading


class Chat:
    def __init__(self, pseudo, host=socket.gethostname(), port=5000):
        self.__pseudo = pseudo
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.bind((host, port))
        self.__s = s
        print('Ecoute sur {}:{}'.format(host, port))

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/quit': self._quit,
            '/join': self._join,
            '/send': self._send,
            '/clients': self._clients
        }
        self.__running = True
        self.__address = None
        self.__servadress = None
        threading.Thread(target=self._receive).start()
        while self.__running:
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ') + 1:].rstrip()
            # Call the command handler
            if command in handlers:
                try:
                    handlers[command]() if param == '' else handlers[command](param)
                except:
                    print("Erreur lors de l'execution de la commande.")
            else:
                print('Command inconnue:', command)

    def _exit(self):
        print('Cya')
        self.__running = False
        self.__servadress = None
        self.__address = None
        self.__s.close()

    def _quit(self):
        if self.__servadress is not None:
            try:
                message = b'/clients' + self.__pseudo.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__servadress)
                    totalsent += sent
                print('Deconnecte du serveur {}:{}'.format(*self.__address))
                self.__servadress = None
            except OSError:
                print('Erreur lors de déconnection au serveur.')

        if self.__address is not None:
            print('Deconnecte de {}:{}'.format(*self.__address))
            self.__address = None

    def _join(self, param):
        self._quit()
        tokens = param.split(' ')
        if len(tokens) == 2:
            try:
                self.__address = (socket.gethostbyaddr(tokens[0])[0], int(tokens[1]))
                print('Connecte a {}:{}'.format(*self.__address))
            except OSError:
                print("Erreur lors de l'envoi du message.")
        else:
            print('Veuillez préciser un port.')

    def _send(self, param):
        if self.__address is not None:
            try:
                message = b'<' + self.__pseudo.encode() + b'>' + param.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__address)
                    totalsent += sent
            except OSError:
                print('Erreur lors de la reception du message.')
        else:
            print('Connectez vous a un client.')

    def _receive(self):
        while self.__running:
            try:
                data, address = self.__s.recvfrom(1024)
                print(data.decode())
            except socket.timeout:
                pass
            except OSError:
                return

    def _clients(self):
        if self.__servadress is not None:
            try:
                message = b'/clients' + self.__pseudo.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__servadress)
                    totalsent += sent
            except OSError:
                print('Erreur lors de la reception du message.')

        else:
            print('Connectez vous a un serveur')

    def _connect(self, param):
        self._quit()
        tokens = param.split(' ')
        if len(tokens) == 2:
            try:
                self.__servadress = (socket.gethostbyaddr(tokens[0])[0], int(tokens[1]))
                print('Connecte au serveur {}:{}'.format(*self.__servadress))
                # envoye le pseudo au serveur
                message = b'/connect' + self.__pseudo.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__servadress)
                    totalsent += sent
            except OSError:
                print("Erreur lors de la connection au serveur.")

    def _help(self):
        pass


if __name__ == '__main__':
    pseudo = input('Votre pseudo: ')
    if len(sys.argv) == 3:
        Chat(pseudo, sys.argv[1], int(sys.argv[2])).run()
    else:
        Chat(pseudo).run()
