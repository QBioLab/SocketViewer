#!python3
import socket
import struct
import numpy as np

#Ref: https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
'''
Version | Commit
 0.1    | First version, by H.F, Oct/08/2019
'''

'''
General class for server and client modules
'''
class general_socket():
    def __init__(self):
        self.PORT = 60000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   
    def recvall(self, sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv( n-len(data))
            if not packet:
                return None
            data += packet
        return data
    
    def send_img(self, sock, img ):
        img_bytes = img.tobytes()
        msg = ( struct.pack('>I', len(img_bytes)) 
                + struct.pack('>H',img.shape[0])
               + struct.pack('>H', img.shape[1]) + img_bytes)
        sock.sendall( msg )
    
    def recv_img(self, sock ):
        raw_msglen = self.recvall( sock, 4 ) # read image length 
        if not raw_msglen:
            print("None data")
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        raw_height = self.recvall( sock, 2)  # raed image height
        height = struct.unpack('>H', raw_height)[0]
        raw_width = self.recvall( sock, 2)   # read image width
        width = struct.unpack('>H', raw_width)[0]
        return (np.frombuffer(self.recvall(sock, msglen),
                              dtype=np.uint16).reshape([height, width]))

                
class socket_server(general_socket):
    def __init__(self):
        super().__init__()
        self.sock.bind(('0.0.0.0', self.PORT))
        self.sock.listen(1)
        
    def connect(self):
        self.conn, addr = self.sock.accept()
        print("Client", addr, "connected")
    
    def send_img(self, img ):
        super().send_img(self.conn, img)
       
    
class socket_viewer(general_socket):
    def __init__(self, HOST):
        super().__init__()
        self.sock.connect((HOST, self.PORT))
        #self.sock.settimeout(0.0)
        
    def recv_img( self ):
        return super().recv_img(self.sock)