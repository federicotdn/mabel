from . import generator
from . import common

ENUM_TEMPLATE = """public enum {name} {{
{values}}}
""" 

CLASS_TEMPLATE = """public class {name}{parent}{extends} {{
{members}}}
"""

IMPORT_TEMPLATE="""import {path};\n"""

TYPE_MAP = {
    common.RecordType.INTEGER: 'int',
    common.RecordType.STRING: 'String',
    common.RecordType.FLOAT: 'float',
    common.RecordType.BOOLEAN: 'boolean',
    common.RecordType.LIST: 'List'
}

class JavaGenerator(generator.Generator):
    def check_unchanged(self, directory):
        filename = self._name + '.java'
        return common.check_cstyle_hash_comment(directory, filename, self._template_hash)
    
    def write_file_start(self, f, package):
        f.write('package ' + package + ';\n\n')

    def save_enum_at(self, directory):
        java = common.create_base_file(directory, self._name, '.java', self._data.get('comment'), self._template_hash)
        package = self._data.get('package')

        values_str = ''
        for i, val in enumerate(self._data['values']):
            values_str += val
            if i != len(self._data['values']) - 1:
                values_str += ',\n'

        values_str = common.incr_indent(values_str)

        enum_str = ENUM_TEMPLATE.format(name=self._name, values=values_str)

        self.write_file_start(java, package)
        java.write(enum_str)

        java.close()

    def save_class_at(self, directory):
        java = common.create_base_file(directory, self._name, '.java', self._data.get('comment'), self._template_hash)
        package = self._data.get('package')

        members_str = ''
        for i, member in enumerate(self._data['members']):
            type_str = common.get_real_type(member['type'], TYPE_MAP)

            m = 'public ' + type_str + ' ' + member['name']
            if 'default' in member:
                m += ' = ' + member['default']
            m += ';'
            if i != len(self._data['members']) - 1:
                m += '\n'
            
            members_str += m

        members_str = common.incr_indent(members_str)

        parent = self._data.get('parent')
        parent_str = '' if not parent else ' extends ' + parent
        
        interface = self._data.get('implements')
        interface_str = '' if not interface else ' implements ' + interface
        
        class_str = CLASS_TEMPLATE.format(name=self._name, members=members_str, parent=parent_str, extends=interface_str)

        if 'Object' in self._used_custom:
            self._used_custom.remove('Object')

        imports_str = ''
        
        used_types = self._used_custom.union(self._used_builtins)
        if parent:
            used_types.add(parent)
        if interface:
            used_types.add(interface)
        if self._name in used_types:
            used_types.remove(self._name)
        
        for used_type in used_types:
            import_str = self.import_for_type(used_type, package)
            if import_str:
                imports_str += import_str
        
        if imports_str:
            imports_str += '\n'

        self.write_file_start(java, package)
        java.write(imports_str)
        java.write(class_str)
        
        java.close()
    
    def import_for_type(self, type_str, my_package):
        path = self.package_for_type(type_str)
        if not path or path == my_package:
            return ''
        return IMPORT_TEMPLATE.format(path=path + '.' + (type_str if type_str != common.RecordType.LIST else TYPE_MAP[type_str]))
    
    def package_for_type(self, type_str):
        if type_str == 'Object':
            return None
        elif type_str == common.RecordType.LIST:
            return 'java.util'
        elif type_str == 'Serializable':
            return 'java.io'
        elif type_str in self._all_templates:
            return self._all_templates[type_str].data['package']
        return None
        
        