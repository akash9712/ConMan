import sys
sys.path.insert(0, '/home/akash/conman_again')

import subprocess
import threading
import subprocess
import pickle
import os
import socket
from multiprocessing import Manager
from creator.log_store import Base_image_tracker, Container_tracker
from creator.creator import ContainerCreator

CONMAN_ROOT = "/home/akash/conman_again"
PORT = 8000
LOG_FILE = os.path.join(CONMAN_ROOT, "logs")
TERMINATE_SOCKET_CONNECTION_MSG = "CLOSE_CONNECTION"

class ContainerManager:
    """
    Class to start, manage and clean-up an existing container. 
    """

    def __init__(self):
        self.__socket__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__manager__ = Manager()
        self.__base_image_tracker__ = Base_image_tracker(self.__manager__)
        self.__container_tracker__ = Container_tracker(self.__manager__)
        self.__container_creator__ = ContainerCreator(self.__base_image_tracker__,
                    self.__container_tracker__)

    def manage(self):
        """
        listen on a port for messages from a process running in a container.
        """
        self.__socket__.bind((socket.gethostname(), PORT))
        self.__socket__.listen(5)

        try:
            while True:
                print("Listening...")
                client_socket, address = self.__socket__.accept()
                message = pickle.loads(client_socket.recv(4096))

                container_name = message['container_name']
                cmd = message['command']
                is_script = message['is_script']

                if not self.__container_tracker__.container_exists(container_name):
                    client_socket.send(bytes("Container does not exist. "
                    "Specify base image for container creation", "utf-8"))
                    base_image_name = pickle.loads(client_socket.recv(4096))['base_image_id']
                    self.__container_creator__.initialize_container(container_name,
                            base_image_name)

                thread = threading.Thread(target=self.run_container,
                        args=(container_name, cmd, message, client_socket), kwargs={"is_script":is_script})
                thread.start()

        except KeyboardInterrupt:
            self.__socket__.close()

    def run_container(self, container, cmd, message, client_socket, is_script=False):
        """
        Kick off the entry point process to run a container.
        """
        print(cmd, flush=True)
        with subprocess.Popen(["sudo",
            os.path.join(CONMAN_ROOT, "cpp/con"), cmd],
            stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                # print(line, end='', flush=True)
                client_socket.send(bytes(line, "utf-8"))
        client_socket.send(bytes(TERMINATE_SOCKET_CONNECTION_MSG, "utf-8"))

def main():
    container_manager = ContainerManager()
    container_manager.manage()
    
if __name__ == '__main__':
    main()