from . import common

class Generator:
    def __init__(self):
        self._data = {}
        self._name = None
        self._used_builtins = None
        self._used_custom = None
        self._config = None
        self._all_templates = []
        self._template_hash = None

    def set_values(self, name, data, template_hash):
        self._name = name
        self._data = data
        self._template_hash = template_hash

    def set_config(self, config, all_templates):
        self._config = config
        self._all_templates = all_templates

    def save_at(self, directory):
        if self.check_unchanged(directory):
            return False
        
        t = self._data['type']
        if t == common.ENUM_RECORD:
            self.save_enum_at(directory)
        elif t == common.CLASS_RECORD:
            self.read_used_types()
            self.save_class_at(directory)
        else:
            raise Exception('Invalid Record Type.')
        
        return True

    def save_enum_at(self, directory):
        raise NotImplementedError()

    def save_class_at(self, directory):
        raise NotImplementedError()

    def check_unchanged(self, directory):
        raise NotImplementedError()

    def read_used_types(self):
        builtins = set()
        custom = set()

        for member in self._data['members']:
            type_str = member['type']

            if type_str in common.RecordTypeList:
                builtins.add(type_str)
            elif common.is_list(type_str):
                subtype = common.get_list_type(type_str)
                builtins.add(common.RecordType.LIST)

                if subtype in common.RecordTypeList:
                    builtins.add(subtype)
                else:
                    custom.add(subtype)
            else:
                custom.add(type_str)

        self._used_builtins = builtins
        self._used_custom = custom