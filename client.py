#!/usr/bin/env python3
# chat.py
# author: Sebastien Combefis et Binome 2
# version: February 15, 2016

import socket
import sys
import threading
import ast


class Chat:
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
        print('Cy@')
        self._quit()
        self.__running = False
        self.__s.close()

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
                print('Erreur lors de deconnection au serveur.')

        if self.__address != None:
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
        elif len(tokens) == 1:
            pseudo = tokens[0]
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
            if self.__address is not None:
                try:
                    data, address = self.__s.recvfrom(1024)
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
                    print("Erreur lors de la connection au serveur.")
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
        print('/send: Envoye un message \n /connect: Connection à un message \n'
              '/join: connection à un autre client (/join + pseudo ou /join + ip + port)'
              ' \n /clients: Reçois la liste des clients \n /quit: Déconnectoin d\'un autre client ou d\'un serveur \n '
              '/exit: Quitter le programme \n ')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        Chat(sys.argv[1], int(sys.argv[2])).run()
    else:
        Chat().run()
