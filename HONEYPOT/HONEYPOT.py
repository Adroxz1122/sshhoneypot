import socket
import paramiko
import threading
import os

honeypot_socket = None

def honeypot_setuper():
    global honeypot_socket
    try:
        honeypot_socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        honeypot_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        honeypot_socket.bind(('YOUR-IP', YOUR_PORT))  #set your IP(as string) and desired port no(as int).
        honeypot_socket.listen(223) # set desired listen no.
    except socket.error as e:
        print(f"socket error : {e}")
    except Exception as e:
        print(f"error : {e}")

def listener_setuper():
    while True:
        try:
            att_sock, att_addr = honeypot_socket.accept()
            attacker_ip, attacker_port = att_addr
            print(f"connection attempt from {att_addr[0]}:{att_addr[1]}")
            t = threading.Thread(target=handle_multiconnections, args=((att_sock,attacker_ip)))
            t.start()
        except Exception as e:
            print(f" Error while accepting connections: {e}")        

def handle_multiconnections(att_sock, attacker_ip):
    try:
        transport = paramiko.Transport(att_sock)
        server_key = paramiko.RSAKey.from_private_key_file('key')
        transport.add_server_key(server_key)
        ssh = SSHSERVER(attacker_ip)
        transport.start_server(server=ssh)
        #ip_add_block()
    except paramiko.SSHException as e:
        print(f"error : {e}")
    except Exception as e:
        print(f"error : {e}")

class SSHSERVER(paramiko.ServerInterface):
    def __init__(self, attacker_ip):
        self.attacker_ip = attacker_ip

    def check_auth_password(self, username: str, password: str) -> int:
        try:
            print(f"{username}:{password}")
            ip_add_block(self.attacker_ip)
        except Exception as e:
            print(f"Error in authentication or blocking: {e}")
        return paramiko.AUTH_FAILED
        
        
    
def ip_add_block(attacker_ip):
    try:
        cmmnd = f"netsh advfirewall firewall add rule name=\"block ip\" dir=in action=block remoteip={attacker_ip}"
        os.system(cmmnd)
        print(f"{attacker_ip} blocked")
    except Exception as e:
        print(f"Error while blocking IP {attacker_ip}: {e}")

if __name__ == "__main__":
    try:
        honeypot_setuper()
        listener_setuper()
    except KeyboardInterrupt:
        print("Honeypot server stopped by user")
    except Exception as e:
        print(f"Unexcepted error in main: {e}")