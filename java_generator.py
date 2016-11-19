import generator
import common

ENUM_TEMPLATE = """public enum {name} {{
{values}}}
""" 

CLASS_TEMPLATE = """public class {name}{parent} {{
{members}}}
"""

TYPE_MAP = {
    common.RecordType.INTEGER: 'int',
    common.RecordType.STRING: 'String',
    common.RecordType.FLOAT: 'float',
    common.RecordType.BOOLEAN: 'boolean',
    common.RecordType.LIST: 'List'
}

class JavaGenerator(generator.Generator):
    def write_file_start(self, f, package):
        f.write('package ' + package + ';\n\n')

    def save_enum_at(self, directory):
        java = common.create_base_file(directory, self._name, '.java')
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
        hpp = common.create_base_file(directory, self._name, '.java')
        package = self._data.get('package')

        members_str = ''
        for i, member in enumerate(self._data['members']):
            type_str = common.get_real_type(member['type'], TYPE_MAP)

            m = 'public ' + type_str + ' ' + member['name'] + ';'
            if i != len(self._data['members']) - 1:
                m += '\n'
            
            members_str += m

        members_str = common.incr_indent(members_str)

        parent = self._data.get('parent')
        parent_str = '' if not parent else ' extends ' + parent
        class_str = CLASS_TEMPLATE.format(name=self._name, members=members_str, parent=parent_str)

        if 'Object' in self._used_custom:
            self._used_custom.remove('Object')

        imports_str = ''
        if common.RecordType.LIST in self._used_builtins:
            imports_str += 'import java.util.List;\n'
        if parent and parent != 'Object':
            imports_str += 'import ' + package + '.' + parent + ';\n'
        for used_custom in self._used_custom:
            if used_custom != self._name and used_custom != parent:
                imports_str += 'import ' + package + '.' + used_custom + ';\n'
        if imports_str:
            imports_str += '\n'

        self.write_file_start(hpp, package)
        hpp.write(imports_str)
        hpp.write(class_str)
        
        hpp.close()