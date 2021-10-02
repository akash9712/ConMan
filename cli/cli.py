#!/home/akash/anaconda3/bin/python3
import argparse
import socket
import pickle

PORT = 8000
TERMINATE_SOCKET_CONNECTION_MSG = "CLOSE_CONNECTION"

def call_daemon_process(args)
    client_socket = socket.socket(AF_INET, SOCK_STREAM)
    message = pickle.dumps({
            container_name: args.container_name,
            command: args.command,
            is_script: args.is_script
        })
    client_socket.send(msg)
    while True:
        msg = client_socket.recv().decode("utf-8")
        if msg == TERMINATE_SOCKET_CONNECTION_MSG:
            client_socket.close()
            break
        print(msg)

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--container-name", help="name of the conatainer to use",
            required=True)
    parser.add_argument("--command", help="command to be run on the container",
            required=True)
    parser.add_arguemnt("--is_script", action=store_false, help="execute command"
                        "as a script")
    
    args = parser.parse_args()
    

if __name__ == '__main__':
    main()