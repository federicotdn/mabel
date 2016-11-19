from . import generator
from . import common

ENUM_TEMPLATE = """enum class {name} {{
{values}}};
""" 

CLASS_TEMPLATE = """struct {name}{parent} {{
{members}}};
"""

TYPE_MAP = {
    common.RecordType.INTEGER: 'uint32_t',
    common.RecordType.STRING: 'std::string',
    common.RecordType.FLOAT: 'float',
    common.RecordType.BOOLEAN: 'bool',
    common.RecordType.LIST: 'std::vector'
}

class CppGenerator(generator.Generator):
    def include_guard_name(self, namespace):
        name = namespace.upper() + "_"
        return name + self._name.upper() + '_H'
    
    def write_file_start(self, f, namespace):
        ig_name = self.include_guard_name(namespace)

        f.write('#ifndef ' + ig_name + '\n')
        f.write('#define ' + ig_name + '\n\n')

    def write_file_end(self, f, namespace):
        f.write('}\n')
        ig_name = self.include_guard_name(namespace)
        f.write('\n#endif //' + ig_name)

    def save_enum_at(self, directory):
        hpp = common.create_base_file(directory, self._name, '.h')
        namespace = self._data.get('namespace')

        values_str = ''
        for i, val in enumerate(self._data['values']):
            values_str += val
            if i != len(self._data['values']) - 1:
                values_str += ',\n'

        values_str = common.incr_indent(values_str)

        enum_str = ENUM_TEMPLATE.format(name=self._name, values=values_str)
        enum_str = common.incr_indent(enum_str)

        self.write_file_start(hpp, namespace)
        hpp.write('namespace ' + namespace + ' {\n')
        hpp.write(enum_str)
        self.write_file_end(hpp, namespace)

        hpp.close()

    def save_class_at(self, directory):
        hpp = common.create_base_file(directory, self._name, '.h')
        namespace = self._data.get('namespace')

        members_str = ''
        for i, member in enumerate(self._data['members']):
            type_str = common.get_real_type(member['type'], TYPE_MAP)

            m = type_str + ' m_' + member['name'] + ';'
            if i != len(self._data['members']) - 1:
                m += '\n'
            
            members_str += m

        members_str = common.incr_indent(members_str)

        parent = self._data.get('parent')
        parent_str = '' if not parent else ' : public ' + parent
        class_str = CLASS_TEMPLATE.format(name=self._name, members=members_str, parent=parent_str)
        class_str = common.incr_indent(class_str)

        includes_str = ''
        if common.RecordType.LIST in self._used_builtins:
            includes_str += '#include <vector>\n'
        if common.RecordType.STRING in self._used_builtins:
            includes_str += '#include <string>\n'
        if parent:
            includes_str += '#include "' + parent + '.h"\n'
        for used_custom in self._used_custom:
            if used_custom != self._name and used_custom != parent:
                includes_str += '#include "' + used_custom + '.h"\n'
        if includes_str:
            includes_str += '\n'

        self.write_file_start(hpp, namespace)
        hpp.write(includes_str)
        hpp.write('namespace ' + namespace + ' {\n')
        hpp.write(class_str)
        self.write_file_end(hpp, namespace)
        
        hpp.close()