""" This class has store, read, delete and dir methods for a simulated disk."""
import threading
import math


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
        self.lock = threading.Lock()
        self.files_on_disk = {}
        self.letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",]
        self.disk_mem = []

        disk_file = open(".storage.txt",'w')
        disk_file.close()
        for i in range(self.size):
            self.disk_mem.append(".")
        print("Block size is %d" % self.blocksize)
        print("Number of blocks is %d" % self.n_blocks)

    def store(self, filename, num_bytes, file_contents, threadID):
        """ Add the specified file to the storage server. """
        self.lock.acquire()
        file_space = int(math.ceil(num_bytes/float(self.blocksize)))
        space = self.get_open_disk_space()
        if(space < file_space):
            self.lock.release()
            return "ERROR: INSUFFICIENT DISK SPACE\n"
        elif filename in self.files_on_disk:
            self.lock.release()
            return "ERROR: FILE EXISTS\n"
        elif(len(file_contents)>num_bytes):
            self.lock.release()
            return "ERROR: FILE CONTENTS LARGER THAN GIVEN BYTE SIZE\n"
        elif(len(self.letters)==0):
            self.lock.release()
            return "ERROR: TOO MANY FILES TO SIMULATE\n"
        else:
            try:
                make_file = open(filename, 'w')
                make_file.write(file_contents)
                make_file.close()
            except:
                self.lock.release()
                return "ERROR: PROBLEM CREATING FILE\n"

            new_file = StoredFiles(filename, self.letters.pop(0), num_bytes, file_space, file_contents)
            disk_file = open(".storage.txt",'a')
            disk_file.write(filename + '\n')
            disk_file.close()
            
            self.files_on_disk[filename] = new_file
            clusters = self.add_file(new_file.letter, file_space)

            print("[thread %d] Stored file '%c' (%d bytes; %d blocks; %d cluster)" % (threadID, new_file.letter, num_bytes, file_space, clusters))
            self.show(threadID)
            print("[thread %d] Sent: ACK" % threadID)
            self.lock.release()
            return "ACK\n"

    def read(self, filename, byte_offset, length, threadID):
        """ Return a list of bytes from the specified offset. """
        self.lock.acquire()
        if filename not in self.files_on_disk:
            self.lock.release()
            return "ERROR: NO SUCH FILE\n"
        read_file = self.files_on_disk[filename]
        if(read_file.num_bytes < byte_offset + length):
            self.lock.release()
            return "ERROR: INVALID BYTE RANGE\n"
        else:
            with open(filename) as f:
                f.seek(byte_offset)
                contents = f.read(length)
            self.lock.release()
            return "ACK %d\n%s\n" % (read_file.num_bytes, contents)

    def delete(self, filename, threadID):
        """ Delete the specified file on the server. """
        self.lock.acquire()
        removed_file = self.files_on_disk.pop(filename)

        # remove file from the directory
        disk_file = open(".storage.txt",'r+')
        files = disk_file.readlines()
        file_exists = True
        disk_file.seek(0)
        for line in files:
            if line != (removed_file.name + '\n'):
                disk_file.write(line)
        disk_file.truncate()
        disk_file.close()

        if not file_exists:
            self.lock.release()
            return "ERROR: NO SUCH FILE\n"
        else:
            i = 0
            j = 0
            while(i<self.size and j<removed_file.num_blocks):
                if(self.disk_mem[i]==removed_file.letter):
                    self.disk_mem[i] = "."
                    j+=1
                i += 1
            print("[thread %d] Deleted %s file '%c' (deallocated %d blocks)" % (threadID, removed_file.name, removed_file.letter, removed_file.num_blocks))
            self.show(threadID)
            self.lock.release()
            return "ACK\n"

    def dir(self, threadID):
        """ Return a list of the filenames in the server."""
        self.lock.acquire()
        disk_file = open(".storage.txt",'r')
        files = disk_file.readlines()
        result = str(len(files)) + '\n' + "".join(files)
        disk_file.close()
        self.lock.release()
        return "%s" % result

    def show(self, threadID):
        """ Print current disk space. """
        print("[thread %d] Simulated Clustered Disk Space Allocation" % threadID)
        line = '=' * 32
        print line
        for i in range(self.size/32):
            print ''.join(self.disk_mem[32*i:32*(i+1)])
        print line

    def get_open_disk_space(self):
        """ Return number of open blocks on disk. """
        count = 0
        for i in range(self.size):
            if self.disk_mem[i]==".":
                count += 1
        return count

    def add_file(self, letter, block_size):
        """ Put file onto disk. """
        cluster = 1
        i = 0
        j = 0

        continuous = True
        while(i<self.size and j<block_size):
            if(self.disk_mem[i]=="."):
                self.disk_mem[i] = letter
                if not continuous:
                    continuous = True
                    cluster += 1
                j+=1
            else:
                continuous = False
            i+=1
        return cluster


class StoredFiles():

    def __init__(self, file_name, letter, num_bytes, num_blocks, contents):
        self.name = file_name
        self.letter = letter
        self.num_bytes = num_bytes
        self.num_blocks = num_blocks
        self.contents = contents