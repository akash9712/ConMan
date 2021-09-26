import os
from creator.log_store import Base_image_tracker, Container_tracker
from multiprocessing import Manager
from subprocess import Popen, PIPE, CalledProcessError
from datetime import datetime
from shutil import rmtree

home = os.path.expanduser("~")
CONMAN_ROOT = f"{home}/conman_again/"
CONTAINERS_BASE_PATH = os.path.join(CONMAN_ROOT, ".containers")
IMAGES_BASE_PATH = os.path.join(CONMAN_ROOT, ".images")

import logging
logging.getLogger().setLevel(logging.INFO)

class Container_creator:
    """
    Class to download, unpack and install image for each container.
    """
    def __init__(self):
        os.makedirs(CONTAINERS_BASE_PATH, exist_ok=True)
        os.makedirs(IMAGES_BASE_PATH, exist_ok=True)
        
        self.__conman_root__ = CONMAN_ROOT
        self.__manager__ = Manager()
        self.__base_image_tracker__ = Base_image_tracker(self.__manager__)
        self.__container_tracker__ = Container_tracker(self.__manager__)
        self.__chroot_dir_names__ = {"bionic": "ubuntu_bionic"}

    def get_base_image_location(self, image_name: str):
        """
        Get location of the base image tarball to be used for creating each container.
        """
        base_image_dict = self.__base_image_tracker__.get_props(image_name)

        if base_image_dict is not None:
            return base_image_dict['image_path']
        return None

    def download_image(self, image_name):
        """
        Download container OS image using debootsrap.
        """
        tarball_download_target = os.path.join(IMAGES_BASE_PATH, image_name+".tar")
        
        download_cmd = f"debootstrap --variant=minbase --make-tarball={tarball_download_target} "\
              f"{image_name} unused_path http://ftp.heanet.ie/pub/ubuntu/"
        self._execute_cmd_(download_cmd)
        self.__base_image_tracker__.add_image(image_name, tarball_download_target)
    
    def extract_image(self, image_name, chroot_path, download_image):
        """
        Extract (unzip) downloaded tarball to Conman execution directory
        """
        base_image_location = self.get_base_image_location(image_name)

        if base_image_location is None:
            if download_image:
                logging.info("Base image not found locally. Downloading now...")
                self.download_image(image_name)
            else:
                raise Exception("Base image not found.")
        os.makedirs(chroot_path, exist_ok=True)

        base_image_location = self.get_base_image_location(image_name)
        extraction_cmd = f"sudo debootstrap --variant=minbase --unpack-tarball={base_image_location} "\
                        f"bionic {chroot_path}"

        self._execute_cmd_(extraction_cmd)

    def initialize_container(self, container_name, image_name, download_image=True):
        """
        Create container instance image.
        """ 
        container_path = os.path.join(CONTAINERS_BASE_PATH, container_name)
        os.makedirs(container_path, exist_ok=True)
        chroot_path = os.path.join(container_path, self.__chroot_dir_names__[image_name])
        
        if self.__container_tracker__.get_props(container_name) is None:
            logging.info("Container not already initialized. Extracting image to initialize a new container.")
            self.extract_image(image_name, chroot_path, download_image)
            self.__container_tracker__.add_container(container_name, image_name, container_path, False, datetime.now(), chroot_path)
        else:
            logging.info(f"Container {container_name} already present.")

    def delete_container(self, container_name):
        
        # Using _execute_cmd because rmtree throwns permission error. 
        deletion_cmd = "sudo rm -rvf {}".format(os.path.join(CONTAINERS_BASE_PATH, container_name))
        self._execute_cmd_(deletion_cmd)
        self.__container_tracker__.remove_props(container_name)

        logging.info(f"Container {container_name} deleted.")

    def _execute_cmd_(self, cmd):
        """
        Execute a command with Popen while continously printing the output
        """
        with Popen(cmd.split(), stdout=PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                print(line, end='')
