from cryptography.hazmat.backends import default_backend  
from cryptography.hazmat.primitives.asymmetric import rsa  
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.fernet import Fernet
import base64
import socket
import threading
import sys
import os

def server_connection(HST,PRT):
    print(f"starting server on {HST}:{PRT}")
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HST, int(PRT)))
    sock.listen(2)
    global conn
    conn, addr = sock.accept()
    print("connected with client")

def client_connection(HST,PRT):
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((HST, int(PRT)))
        print(f"connected to server at {HST}:{PRT}")
    except:
        print("error connecting to server")
        sys.exit()

def gen_sym_key(data):
    global sym_key, FR
    if data == "server":
        sym_key = Fernet.generate_key()
    else:
        sym_key = data
    FR = Fernet(sym_key)

def sym_encrypt(data):
    b64_data = base64.b64encode(data.encode('utf-8'))
    return(FR.encrypt(b64_data))
    
def sym_decrypt(data):
    plaintext_b64 = FR.decrypt(data)
    return(base64.b64decode(plaintext_b64).decode())
    
def gen_asym_keys():
    global private_key, public_key, private_pem, public_pem
    private_key = rsa.generate_private_key(public_exponent=65537,key_size=4096,backend=default_backend())
    public_key = private_key.public_key() 
    private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL,encryption_algorithm=serialization.NoEncryption())
    public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

def import_key(data):
    global client_key
    client_key = load_pem_public_key(data,backend=default_backend())

def asym_encrypt(data):
    return(client_key.encrypt(data,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None)))

def asym_decrypt(data):
    return(private_key.decrypt(data,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None)))
    

def server_exchange():
    print("exchanging keys with client")
    while True:
        conn.send(public_pem)
        data = conn.recv(10240).decode()
        if "-----BEGIN PUBLIC KEY-----" in data:
            import_key(data.encode('utf-8'))
            break
        else:
            pass
    aes_key = asym_encrypt(sym_key)
#    sym_key_data = f"===AES_KEY===\n{aes_key}".encode('utf-8')
#    while True:
    conn.send(aes_key)
#    data = conn.recv(10240).decode()
#    if "===OK===" in data:
    print("exchanged keys with client")
#            break
#        else:
#            pass

def client_exchange():
    print("exhanging keys with server")
    while True:
        data = conn.recv(10240).decode()
        if "-----BEGIN PUBLIC KEY-----" in data:
            import_key(data.encode('utf-8'))
            conn.send(public_pem)
            break
        else:
            pass
    while True:
        data = conn.recv(10240)
        if len(data) > 10:
            aes_key = asym_decrypt(data)
            gen_sym_key(aes_key)
            conn.send("===OK===".encode('utf-8'))
            print("exchanged keys with server")
            break
        else:
            pass

def checkstr(data):
    outstr = ""
    if "===MSG===" in data:
        for ln in data.split("\n"):
            if "===MSG===" in ln:
                pass
            else:
                outstr += ln
        return(sym_decrypt(outstr.encode()))
    else:
        return("1")

def recv():
    while True:
        data = conn.recv(10240)
        if "MSG" in data.decode():
            msg = sym_decrypt(data.decode().split("|||")[1].encode('utf-8'))
            print(f"\nMESSAGE: {msg}\n")
        else:
            pass
    
def chat():
    print("the interface is bare bones,\njust type what you want to say and hit enter\n\n")
    while True:
        msg = input(" ")
        cyphertext = "MSG|||{}".format(sym_encrypt(msg).decode()).encode('utf-8')
        conn.send(cyphertext)

def main_server():
    gen_asym_keys()
    gen_sym_key("server")
    HST = input("\nhost: ")
    PRT = input("\nport: ")
    server_connection(HST,PRT)
    server_exchange()
    print("session started")
    t1 = threading.Thread(target=chat)
    t2 = threading.Thread(target=recv)
    t1.start()
    t2.start()

def main_client():
    gen_asym_keys()
    HST = input("\nhost: ")
    PRT = input("\nport: ")
    client_connection(HST,PRT)
    client_exchange()
    print("session started")
    t1 = threading.Thread(target=chat)
    t2 = threading.Thread(target=recv)
    t1.start()
    t2.start()
        
def main():
    os.system("clear")
    option = input("client\t[C]\nserver\t[S]\noption: ")
    if option.lower() == "s":
        main_server() 
    else:
        main_client()

main()
