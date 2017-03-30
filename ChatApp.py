#!/usr/bin/env python3
# chat.py
# author: Sebastien Combefis et Binome 2
# version: February 30, 2017

import socket
import sys
import threading
import ast


class Client:
    def __init__(self, host=socket.gethostname(), port=4269):
        self.__pseudo = str(input('Votre pseudo: '))
        self.__avlbl = None
        self.__update = False
        self.__running = True
        self.__address = None
        self.__servaddress = None
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.bind((host, port))
        self.__s = s
        print('Ecoute sur {}:{} en tant que {}'.format(host, port, self.__pseudo))
        print('Tapez /help pour avoir de l\'aide')

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/quit': self._quit,
            '/join': self._join,
            '/send': self._send,
            '/clients': self._clients,
            '/connect': self._connect,
            '/help': self._help
        }
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
        self._quit()
        self.__running = False
        self.__s.close()
        print('Cy@')

    def _quit(self):
        if self.__servaddress is not None:
            try:
                message = b'/quit ' + self.__pseudo.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__servaddress)
                    totalsent += sent
                print('Deconnecte du serveur {}:{}'.format(*self.__servaddress))
                self.__servaddress = None
            except OSError:
                print('Erreur lors de deconnexion au serveur.')

        if self.__address != None:
            print('Deconnecte de {}:{}'.format(*self.__address))
            self.__address = None

    def _join(self, param):
        self._quit()
        tokens = param.split(' ')
        if len(tokens) == 3 and tokens[0] == '-ip':
            try:
                self.__address = (socket.gethostbyaddr(tokens[1])[0], int(tokens[2]))
                print('Connecte a {}:{}'.format(*self.__address))
            except OSError:
                print("Erreur lors de l'envoi du message.")
        elif tokens[0] == '-p':
            pseudo = tokens[1]
            if pseudo in self.__avlbl:
                self.__address = (socket.gethostbyaddr(self.__avlbl[pseudo][0])[0], int(self.__avlbl[pseudo][1]))
                print('Connecte a {} sur {}:{}'.format(pseudo, *self.__address))

    def _send(self, param):
        if self.__address is not None:
            try:
                message = b'<' + self.__pseudo.encode() + b'>: ' + param.encode()
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
                if address[1] != 4200:
                    print(data.decode())
            except socket.timeout:
                pass
            except OSError:
                return

    def _clients(self):
        if self.__servaddress is not None:
            try:
                message = b'/clients ' + self.__pseudo.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__servaddress)
                    totalsent += sent
            except OSError:
                print('Erreur lors de la reception du message.')
            while self.__update is False:
                try:
                    data, address = self.__s.recvfrom(1024)
                    self.__avlbl = ast.literal_eval(data.decode())
                    self._printdic(self.__avlbl)
                    self.__update = True
                except socket.timeout:
                    pass
                except OSError:
                    return
            self.__update = False

        else:
            print('Connectez vous a un serveur')

    def _connect(self, param):
        self._quit()
        data = b'0'
        # data is 0 if the nickname is already taken. 1 if not.
        while data == b'0':
            tokens = param.split(' ')
            if len(tokens) == 2:
                try:
                    self.__servaddress = (socket.gethostbyaddr(tokens[0])[0], int(tokens[1]))
                    # envoye le pseudo au serveur
                    message = b'/connect ' + self.__pseudo.encode()
                    totalsent = 0
                    while totalsent < len(message):
                        sent = self.__s.sendto(message[totalsent:], self.__servaddress)
                        totalsent += sent
                    while self.__update is False:
                        try:
                            data, address = self.__s.recvfrom(1024)
                            if data == b'0':
                                self.__pseudo = str(input('Votre pseudo est deja pris, veuillez entrer un nouveau: '))
                            self.__update = True
                        except socket.timeout:
                            pass
                    print('Connecte au serveur {}:{}'.format(*self.__servaddress))
                    self.__update = False

                except OSError:
                    print("Erreur lors de la connexion au serveur.")
                    break
            else:
                print('veuillez entrer une adresse valide')
                break

    def _printdic(self, dico):
        result = ''
        for e in dico:
            result += e + ": à l'adresse " + dico[e][0] + ' et au port ' + str(dico[e][1]) + '\n'
        print(result)

    def _help(self):
        print(' /send: Envoye un message \n /connect: Connexion à un serveur \n '
              '/join: Connexion à un autre client (/join + "-p" + pseudo ou /join + "-ip" + ip + port)'
              ' \n /clients: Reçois la liste des clients \n /quit: Déconnexion d\'un autre client ou d\'un serveur \n '
              '/exit: Quitter le programme \n ')


class Server:
    def __init__(self, host=socket.gethostname(), port=4200):
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.bind((host, port))
        self.__s = s
        print('Ecoute sur {}:{}'.format(host, port))
        self.__clients = {}

    def run(self):
        handlers = {
            '/exit': self._exit,
        }
        self.__running = True
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
        for i in self.__clients:
            self._send(self.__clients[i], "the server is now closed \n XOXO")
        self.__running = False
        self.__s.close()

    def _send(self, address, param):
        try:
            message = param.encode()
            totalsent = 0
            while totalsent < len(message):
                sent = self.__s.sendto(message[totalsent:], address)
                totalsent += sent
        except OSError:
            print('Erreur lors de la reception du message.')

    def _receive(self):
        while self.__running:
            try:
                data, address = self.__s.recvfrom(1024)
                line = data.decode()
                # Extract the command and the param
                print('Reçu:', line)
                command = line[:line.index(' ')]
                pseudo = line[line.index(' ') + 1:].rstrip()
                if command == '/clients':
                    self._send(address, str(self.__clients))
                if command == '/connect':
                    if pseudo in self.__clients:
                        self._send(address, "0")
                        print('Pseudo existant')
                    else:
                        self.__clients[pseudo] = (address[0], 4269)
                        self._send(address, "1")
                        print('{} connecté'.format(pseudo))
                if command == '/quit':
                    self.__clients.pop(pseudo)
                    print('{} déconnecté'.format(pseudo))
            except socket.timeout:
                pass
            except OSError:
                return


if __name__ == '__main__':
    if sys.argv[1] == 'server':
        Server().run()
    else:
        Client().run()
