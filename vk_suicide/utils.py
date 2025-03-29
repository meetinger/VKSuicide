from charset_normalizer import from_path

class AutoOpen:
    def __init__(self, file_path, mode='r'):
        self.file_path = file_path
        self.mode = mode
        self.file = None

    def __enter__(self):
        result = from_path(self.file_path).best()
        self.encoding = result.encoding

        self.file = open(self.file_path, self.mode, encoding=self.encoding)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file:
            self.file.close()
