import socket, sys, threading

SERVER=True
PEER=("10.0.0.2", 6222)
LOCALVPN=("localhost", 6220)

EXT=("10.0.0.1", 6222)
INT=("localhost", 6221)

#Immer 0
LOCALVPNPORT=0

#try:
socket_int_rec = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_int_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_int_rec.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_int_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#socket_int.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
socket_int_rec.bind(INT)
socket_int_send.bind((INT[0], (INT[1]-1)))
#except:
    #print ("Could not set up INT socket.")
    #sys.exit(1)

#try:
socket_ext_rec = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_ext_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_ext_rec.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_ext_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#socket_ext.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
socket_ext_rec.bind(EXT)
socket_ext_send.bind(EXT)



#socket_int_rec2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#socket_int_rec2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#socket_int_rec2.bind(INT)

#except:
    #print ("Could not set up EXT socket.")
    #sys.exit(1)

def int_to_ext():
    global LOCALVPNPORT
    global SERVER
    global LOCALVPN
    global socket_int_rec
    global socket_ext_send
    while True:
        data, addr = socket_int_rec.recvfrom(4096)
        if(not SERVER):
            LOCALVPNPORT=addr[1]
        socket_ext_send.sendto(data, PEER)
        print("int to ext")

def ext_to_int():
    global LOCALVPNPORT
    global SERVER
    global LOCALVPN
    global socket_int_send
    global socket_ext_rec
    while True:
        data, addr = socket_ext_rec.recvfrom(4096)
        if(not SERVER):
            socket_int_send.sendto(data, ("localhost", LOCALVPNPORT))
        if(SERVER):
            socket_int_send.sendto(data, LOCALVPN)
        print("ext to int")



t_int_to_ext = threading.Thread(target=int_to_ext)
t_ext_to_int = threading.Thread(target=ext_to_int)
t_int_to_ext.start()
t_ext_to_int.start()