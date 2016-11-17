import generator
import common

ENUM_TEMPLATE = """enum class {name} {{
{values}}};
""" 

CLASS_TEMPLATE = """class {name}{parent} {{
{members}}};
"""

TYPE_MAP = {
    'int': 'uint32_t',
    'string': 'std::string',
    'float': 'float',
    'bool': 'bool',
    'list': 'std::vector'
}

class CppGenerator(generator.Generator):
    def include_guard_name(self, namespace):
        name = '' if not namespace else namespace.upper() + "_"
        return name + self._name.upper() + '_H'
    
    def write_file_start(self, f, namespace):
        ig_name = self.include_guard_name(namespace)

        f.write('#ifndef ' + ig_name + '\n')
        f.write('#define ' + ig_name + '\n\n')

    def write_file_end(self, f, namespace):
        if namespace:
            f.write('}\n')

        ig_name = self.include_guard_name(namespace)
        f.write('\n#endif //' + ig_name)

    def save_enum_at(self, directory):
        hpp = common.create_base_file(directory, self._name, '.h')
        namespace = self._data.get('namespace')

        self.write_file_start(hpp, namespace)
        if namespace:
            hpp.write('namespace ' + namespace + ' {\n')

        values_str = ''
        for i, val in enumerate(self._data['values']):
            values_str += val
            if i != len(self._data['values']) - 1:
                values_str += ',\n'

        values_str = common.incr_indent(values_str)

        enum_str = ENUM_TEMPLATE.format(name=self._name, values=values_str)
        if namespace:
            enum_str = common.incr_indent(enum_str)

        hpp.write(enum_str)

        self.write_file_end(hpp, namespace)
        hpp.close()

    def save_class_at(self, directory):
        hpp = common.create_base_file(directory, self._name, '.h')
        namespace = self._data.get('namespace')

        using_string = False
        using_vector = False

        members_str = ''
        for i, member in enumerate(self._data['members']):
            if member['type'] == 'string':
                using_string = True

            type_str = TYPE_MAP.get(member['type'])

            m = 'public ' + type_str + ' ' + member['name'] + ';'
            if i != len(self._data['members']) - 1:
                m += '\n'
            
            members_str += m


        self.write_file_start(hpp, namespace)
        if using_string:
            hpp.write('#include <string>\n\n')
        
        if namespace:
            hpp.write('namespace ' + namespace + ' {\n')

        members_str = common.incr_indent(members_str)

        parent = self._data.get('parent')
        parent_str = '' if not parent else ' : public ' + parent
        class_str = CLASS_TEMPLATE.format(name=self._name, members=members_str, parent=parent_str)

        if namespace:
            class_str = common.incr_indent(class_str)

        hpp.write(class_str)

        self.write_file_end(hpp, namespace)
        hpp.close()