import common

class ClassMember:
    def __init__(self):
        self._type = None
        self._name = None

class Generator:
    def __init__(self):
        self._data = {}
        self._name = None

    def set_values(self, name, data):
        self._name = name
        self._data = data

    def save_at(self, directory):
        t = self._data['type']
        if t == common.ENUM_RECORD:
            self.save_enum_at(directory)
        elif t == common.CLASS_RECORD:
            self.save_class_at(directory)
        else:
            raise Exception('Invalid Record Type.')

    def save_enum_at(self, directory):
        raise NotImplementedError()

    def save_class_at(self, directory):
        raise NotImplementedError()

    def get_class_members(self):
        pass