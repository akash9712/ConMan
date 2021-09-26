import subprocess
from socket import socket, gethostname, AF_INET, SOCK_STREAM
from dataclass import dataclass

CONMAN_ROOT = "$HOME/conman_again"
PORT = 8000
LOG_FILE = os.path.join(CONMAN_ROOT, "logs")

@dataclass(unsafe_hash=True)
class Container:
    entry_script: string
    container_id: string

class Manager:
    """
    Class to start, manage and clean-up an existing container. 
    """

    def __init__(self, container, logger):
        self.__logger__ = logger
        self.__socket__ = socket(AF_INET, SOCK_STREAM)
        self.__socket__ = socket(AF_INET, SOCK_STREAM)
        self.__log_fie__ = LOG_FILE

    def listen_on_port(self, port_number: int, container_id):
        """
        listen on a port for messages from a process running in a container.
        """
        self.__socket__.bind((gethostname(), PORT))
        self.__socket_.listen(5)

        while True:
            client_socket, address = self.__socket__.accept()

    def update_logs(self):
        """
        Update logs for the container.
        """
        pass

    def clean_up(self, container_name):
        """
        Clean up once a container terminates after it's entry point process terminates.
        """
        pass

    @static_method
    def start_entry_point_process(cmd, script=True):
        """
        Kick off the entry point process to run a container.
        """
        pass
