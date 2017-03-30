#! / usr / bin / env
# python3
# chat.py
# author: Sebastien Combefis
# version: February 15, 2016

import socket
import sys
import threading


class server:
    def __init__(self, host=socket.gethostname(), port=5000):
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
                data.decode()
                command = data[:data.index(' ')]
                pseudo = data[data.index(' ') + 1:].rstrip()
                if command == '/clients':
                    self._send(self.__clients[pseudo], self._clients())
                if command == '/connect':
                    if pseudo in self.__clients:
                        self._send(self.__clients[pseudo], "0")
                    else:
                        self.__clients[pseudo] = address
                        self._send(self.__clients[pseudo], "1")
                if command == '/quit':
                    self.__clients.pop(pseudo)
            except socket.timeout:
                pass
            except OSError:
                return

    def _clients(self):
        clientlist= ""
        for i in self.__clients:
            clientlist += i + " - " + self.__clients[i] + "\n"
        return clientlist


if __name__ == '__main__':
    if len(sys.argv) == 3:
        server(sys.argv[1], int(sys.argv[2])).run()
    else:
        server().run()