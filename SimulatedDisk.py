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

    def __init__(self, size=256):
        self.size = size
        self.lock = threading.Lock()
        pass


    def store(self, filename, num_bytes, file_contents):
        """ Add the specified file to the storage server. """
        self.lock.acquire()
        self.lock.release()
        return "PLACEHOLDER RESULT OF STORE METHOD\n"

    def read(self, filename, byte_offset, length):
        """ Return a list of bytes from the specified offset """
        self.lock.acquire()
        self.lock.release()
        return "PLACEHOLDER RESULT OF READ METHOD\n"

    def delete(self, filename):
        """ Delete the specified file on the server. """
        self.lock.acquire()
        self.lock.release()
        return "PLACEHOLDER RESULT OF DELETE METHOD\n"

    def dir(self):
        """ Return a list of the filenames in the server."""
        self.lock.acquire()
        self.lock.release()
        return "PLACEHOLDER RESULT OF DIR METHOD\n"

