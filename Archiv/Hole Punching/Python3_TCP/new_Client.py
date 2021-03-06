__author__ = 'Alexander Mark, FireVPN'

import socket
import pickle
import threading
import logging
from datetime import datetime
import time

#Logik des Hole Puncher
class Client():

    #Konstruktor, Adresse des Hosts einlesen, log file anlegen und initialisieren
    def __init__(self):
        filename="tcp_hole_puncher_client"+str(datetime.now())+".log"
        logging.basicConfig(filename=filename,level=logging.DEBUG)
        logging.debug("created file at "+str(datetime.now()))
        print ("starting programm...")
        logging.debug("starting programm")
        self.ip=input("IP des Hosts: ")
        self.port=int(input("Port des Hosts: "))
        print("IP + Port from Host saved")
        logging.debug("local tcp socket choosen address "+self.ip+":"+str(self.port))

    #Verbindung zu Server herstellen
    def connect_to_server(self):
        self.srv_ip=input("IP des Servers: ")
        self.srv_port=int(input("Port des Servers: "))
        print ("Got Server Adress")
        logging.debug("Adress of Roundevouz Server "+self.srv_ip+":"+str(self.srv_port))

        self.to_srv_sock = socket.socket()

        self.to_srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Addresse wieder verwenden
        self.to_srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) #Port wieder verwenden

        self.to_srv_sock.bind((self.ip, self.port)) #IP + Port "zusammenfuehren"
        print("Set up Socket (for Server Communication)")
        logging.debug("tcp socket for server communication set up, with address and port reuse")

        while(self.to_srv_sock.connect_ex((self.srv_ip, self.srv_port))): #SYN packets flooding
            pass
        print("connected to Server!")
        logging.debug("connected to server")

    #Befehl zu Server senden (send list, refresh,...)
    def send_command_to_srv(self):
        print("#Mögliche Befehle: \n"
              "#R: Adressen von Server erhalten")
        logging.debug("displayed possible commands")
        self.command=input("Command for Server-Interaktion: ")
        self.to_srv_sock.send(self.command.encode('utf-8'))
        print (self.command, "send to Server")
        logging.debug("user selected "+self.command)

        if self.command=='R':
            self.receive_from_srv()
            logging.debug("waiting for reply/data from server")

    #von Server empfangen (informationen)
    def receive_from_srv(self):
        data =self.to_srv_sock.recv(1024)
        print ("received data from Server")
        logging.debug("received data from server")
        self.available_adresses=pickle.loads(data)
        if len(self.available_adresses)==1:
            print("your Adress", self.available_adresses, "no others found, going back to command mode")
            logging.debug("only one adress got => nobody out there"+str(self.available_adresses)+"\n going back to command mode")
            self.send_command_to_srv()
        else:
            logging.debug("more than one address got, user have to choose one"+str(self.available_adresses))
            self.choose_addr()

    #addresse ausaehlen
    def choose_addr(self):
        print ("#available Adresses:")
        for i in self.available_adresses:
            print (i)
        selected_adr=input("gewünschte Adresse (IP:Port): ")
        splited_adress=selected_adr.split(":")
        logging.debug("selected adress: "+selected_adr)
        self.selected_ip=splited_adress[0]
        self.selected_port=int(splited_adress[1])
        self.handle_punch()


    #hole punching prozess starten
    def handle_punch(self):
        self.connection_accepted=False
        logging.debug("prepareing punch, starting thread with destination address selected from address as destination and a listening socket")
        self.syn_flooding=threading.Thread(target=self.connect_to_Client)
        self.listen_syn=threading.Thread(target=self.listen_for_Client_connection)
        self.syn_flooding.start()
        logging.debug("syn flooding started")
        self.listen_syn.start()
        logging.debug("listening for incoming syn flooding started")

        logging.debug("waiting 3 seconds")
        self.connection_accepted=False
        time.sleep(3)

        logging.debug("Checking result of punch")
        if (self.connection_accepted):
            logging.debug("Worked fine")
        else:
            logging.debug("bad result, stopping threads and decreasing ports")
            self.syn_flooding.kill()
            self.listen_syn.kill()

            #port-1 setzen, siehe nat heuristik
            self.selected_port=self.selected_port-1
            logging.debug("starting Threads again, with port-1")
            self.syn_flooding=threading.Thread(target=self.connect_to_Client)
            self.listen_syn=threading.Thread(target=self.listen_for_Client_connection)
            self.syn_flooding.start()
            logging.debug("syn flooding started")
            self.listen_syn.start()
            logging.debug("listening for incoming syn flooding started")

            logging.debug("listening for incoming syn flooding started")
            logging.debug("waiting 3 seconds")
            self.connection_accepted=False
            time.sleep(3)

            if (self.connection_accepted):
                logging.debug("Worked fine")
            else:
                logging.debug("bad result, stopping threads and increasing ports")
                self.syn_flooding.kill()
                self.listen_syn.kill()

                #port (orginal) +1 setzen, siehe NAT heuristik
                self.selected_port=self.selected_port+2
                logging.debug("starting Threads again, with port+1")
                self.syn_flooding=threading.Thread(target=self.connect_to_Client)
                self.listen_syn=threading.Thread(target=self.listen_for_Client_connection)
                self.syn_flooding.start()
                logging.debug("syn flooding started")
                self.listen_syn.start()
                logging.debug("listening for incoming syn flooding started")

                logging.debug("listening for incoming syn flooding started")
                logging.debug("waiting 3 seconds")
                self.connection_accepted=False
                time.sleep(3)


                if (self.connection_accepted):
                    logging.debug("Worked fine")
                else:
                    logging.debug("no success, stopping threads trying to relay")
                    print("no sucess, trying to relay")
                    self.syn_flooding.kill()
                    self.listen_syn.kill()
                    #"orginale" port
                    self.selected_port=self.selected_port-1
                    #start relaying



    def connect_to_Client(self):
        print ("intialising connection Socket for Client")
        logging.debug("intialising connection Socket (syn flooding) for Client")
        connect_socket = socket.socket()

        connect_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Addresse wieder verwenden
        connect_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) #Port wieder verwenden

        connect_socket.bind((self.ip, self.port)) #IP + Port "zusammenfuehren"
        print ("connection Socket set up")
        logging.debug("set up tcp socket for syn flooding, address and port reuse used")
        while(connect_socket.connect_ex((self.selected_ip, self.selected_port))): #SYN packets flooding
            pass
        self.connection_accepted=True
        self.listen_syn.kill()
        print("connected!")
        logging.debug("connected to other host! logged from conncet/syn flooding socket, other Thread stopped")
        #was nun?
        #ovpn starten?

    def listen_for_Client_connection(self):
        print ("intialising listening Socket for Client")
        logging.debug("intialising listening Socket (for acceoting connection) for Client")
        listen_socket = socket.socket()

        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Addresse wieder verwenden
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) #Port wieder verwenden

        listen_socket.bind((self.ip, self.port ))#IP + Port "zusammenfuehren"
        print ("listen Socket set up")
        listen_socket.listen(5) #listen starten, auf das SYN flooding warten
        logging.debug("set up tcp socket for accepting syn packets, address and port reuse used")
        listen_socket.accept() # Verbindung annehmen
        self.connection_accepted=True
        self. syn_flooding.kill()
        logging.debug("connected to other host! logged from listening socket syn accepted, other thread stopped")
        print("connected!")
        #was nun?
        #ovpn starten?

def main():
    client=Client()
    client.connect_to_server()
    client.send_command_to_srv()
    #socket erhalten (der mit dem anderen client verbunden ist und diesen dem Proxy übergeben => neue klasse)


if __name__ == '__main__':
    main()

