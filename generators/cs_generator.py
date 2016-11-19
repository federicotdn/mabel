from . import generator
from . import common

ENUM_TEMPLATE = """enum {name} {{
{values}}}
""" 

CLASS_TEMPLATE = """class {name}{parent} {{
{members}}}
"""

TYPE_MAP = {
    common.RecordType.INTEGER: 'int',
    common.RecordType.STRING: 'string',
    common.RecordType.FLOAT: 'float',
    common.RecordType.BOOLEAN: 'bool',
    common.RecordType.LIST: 'List'
}

class CsGenerator(generator.Generator):
    def save_enum_at(self, directory):
        cs = common.create_base_file(directory, self._name, '.cs')
        namespace = self._data.get('namespace')

        values_str = ''
        for i, val in enumerate(self._data['values']):
            values_str += val
            if i != len(self._data['values']) - 1:
                values_str += ',\n'

        values_str = common.incr_indent(values_str)

        enum_str = ENUM_TEMPLATE.format(name=self._name, values=values_str)
        enum_str = common.incr_indent(enum_str)
        
        cs.write('namespace ' + namespace + ' {\n')
        cs.write(enum_str)
        cs.write('}\n')

        cs.close()

    def save_class_at(self, directory):
        cs = common.create_base_file(directory, self._name, '.cs')
        namespace = self._data.get('namespace')

        members_str = ''
        for i, member in enumerate(self._data['members']):
            type_str = common.get_real_type(member['type'], TYPE_MAP)

            m = 'public ' + type_str + ' ' + member['name'] + ';'
            if i != len(self._data['members']) - 1:
                m += '\n'
            
            members_str += m

        members_str = common.incr_indent(members_str)

        parent = self._data.get('parent')
        parent_str = '' if not parent else ' : ' + parent
        class_str = CLASS_TEMPLATE.format(name=self._name, members=members_str, parent=parent_str)
        class_str = common.incr_indent(class_str)

        if 'object' in self._used_custom:
            self._used_custom.remove('object')

        imports_str = ''
        if common.RecordType.LIST in self._used_builtins:
            imports_str += 'using System.Collections.Generic;\n\n'

        cs.write(imports_str)
        cs.write('namespace ' + namespace + ' {\n')
        cs.write(class_str)
        cs.write('}\n')

        cs.close()