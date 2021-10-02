import os
import pickle
from ilock import ILock
from multiprocessing import Manager

home = os.path.expanduser("~")
IMAGE_TRACKER_PATH = f"{home}/conman_again/.images/image_tracker"
CONTAINER_TRACKER_PATH = f"{home}/conman_again/.containers/container_tracker"


class Tracker:
    """
    Base class for state trackers.
    """
    def __init__(self, manager, tracker_path):
        # multiprocess safe dictionary
        self.__tracker_dict__ = manager.dict()
        if not os.path.isfile(tracker_path):
            with open(tracker_path, 'wb') as handle:
                pickle.dump(dict(self.__tracker_dict__), handle, pickle.HIGHEST_PROTOCOL)
        else:
            with open(tracker_path, 'rb') as handle:
                self.__tracker_dict__.update(pickle.load(handle))

        self.__tracker_path__ = tracker_path

    def get_props(self, key):
        return self.__tracker_dict__.get(key, None)

    def add_props(self, key, val_dict):
        # System-wide mutex lock on file
        with ILock('base_image_track_file_lock'):
            self.__tracker_dict__.update({key: val_dict})
            with open(self.__tracker_path__, 'wb') as handle:
                pickle.dump(dict(self.__tracker_dict__), handle, pickle.HIGHEST_PROTOCOL)

    def remove_props(self, key):
        self.__tracker_dict__.pop(key)
        with ILock('base_image_track_file_lock'):
            with open(self.__tracker_path__, 'wb') as handle:
                pickle.dump(dict(self.__tracker_dict__), handle, pickle.HIGHEST_PROTOCOL)


class Base_image_tracker(Tracker):
    """
    Tracking base images.
    Dict schema: {image_name: {image_path: path}}
    """

    def __init__(self, manager, *args):
        super().__init__(manager, IMAGE_TRACKER_PATH)

    def add_image(self, image_name, image_path):
        self.add_props(image_name, {"image_path": image_path})

    def base_image_exists(self, image_name):
        return self.__tracker_dict__.get(image_name, False)


class Container_tracker(Tracker):
    """
    Tracking all initialized, non-deleted containers.
    Dict Schema: {
        container_name: {
            image_name: str,
            container_location: str,
            running: bool,
            creation_time: datetime.datetime,
            chroot_dir: str
            }
        }
    """

    def __init__(self, manager, *args):
        super().__init__(manager, CONTAINER_TRACKER_PATH)

    def add_container(self, container_name, image_name, container_location, running, creation_time, chroot_dir):
        val_dict = {
            "image_name": image_name,
            "container_location": container_location,
            "running": running,
            "creation_time": creation_time,
            "chroot_dir": chroot_dir
        }
        self.add_props(container_name, val_dict)

    def container_exists(self, container_name):
        return self.__tracker_dict__.get(container_name, False)
