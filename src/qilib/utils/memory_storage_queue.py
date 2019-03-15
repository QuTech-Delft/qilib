from queue import Queue


class MemoryStorageQueue(Queue):
    DATA = 'data'
    META_DATA = 'meta_data'
    ARRAY = 'array'

    def add_data(self, *data):
        self.put((self.DATA, data))

    def add_meta_data(self, *meta_data):
        self.put((self.META_DATA, meta_data))

    def add_array(self, array):
        self.put((self.ARRAY, array))
