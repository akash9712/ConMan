#!/home/akash/anaconda3/bin/python3
import argparse
from conman_again.daemon import Container, Manager
from conman_again.creator import Container_creator

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-create-container", action="store_true")
    parser.add_argument("-container-name", help="name of the container to be created.")
    parser.add_argument("-script-location", help="name of the script to be used as an entry point to the container")

    args = parser.parse_args()
    if(args.create_container):
        container_creator.initialize_container(args.container_name)
    else:
        daemon.start_entry_point_proces()


if __name__ == '__main__':
    main()