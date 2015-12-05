""" This class has store, read, delete and dir methods for a simulated disk."""
import threading


class SimulatedDiskError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

"""
Here's how to use this error to send error messages back to the client.

if ERROR:
    raise SimulatedDiskError("ERROR: <error-description>\n")

these will be caught by the server and sent to the client.

"""

class SimulatedDisk():

    def __init__(self, size=256, n_blocks=128, blocksize=4096):
        self.size = size
        self.n_blocks = n_blocks
        self.blocksize = blocksize
        self.lock = threading.Lock
        self.disk_mem = []
        self.disk_file = open("disk.txt",'w')
        self.disk_file.close()
        for i in range(self.size):
            self.mem.append(".")

    def store(filename, num_bytes, file_contents):
        """ Add the specified file to the storage server. """
        self.lock.acquire()
        self.lock.release()

    def read(filename, byte_offset, length):
        """ Return a list of bytes from the specified offset """
        self.lock.acquire()
        self.lock.release()

    def delete(filename):
        """ Delete the specified file on the server. """
        self.lock.acquire()
        self.lock.release()

    def dir():
        """ Return a list of the filenames in the server."""
        self.lock.acquire()
        self.lock.release()
        return "0\n"

