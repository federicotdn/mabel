from . import generator
from . import common

ENUM_TEMPLATE = """enum class {name} {{
{values}}};

static const size_t {name}Count = {count};
""" 

CLASS_TEMPLATE = """struct {name}{parent} {{
{members}{serialization}}};
"""

SET_TEMPLATE = """
void set(const {type}& other) {{
{set}}}"""

SET_LIST_TEMPLATE = """for (const {subtype}& otherItem : other.{member}) {{
{submember_set}}}"""

SAVE_TEMPLATE = """
void saveBinary(BitBuffer& buffer) {{
{save}}}"""

SAVE_INTEGER_TEMPLATE = """buffer.putInt({member});"""
SAVE_STRING_TEMPLATE = """buffer.putString({member});"""
SAVE_FLOAT_TEMPLATE = """buffer.putFloat({member});"""
SAVE_BOOLEAN_TEMPLATE = """buffer.putBit({member});"""
SAVE_LIST_TEMPLATE = """buffer.putInt({member}.size());
for ({subtype}& item : {member}) {{
{submember_save}}}"""
SAVE_ENUM_TEMPLATE = """buffer.putEnum((uint32_t) {member}, (uint32_t) {type}Count);"""
SAVE_CLASS_TEMPLATE = """{member}.saveBinary(buffer);"""

LOAD_TEMPLATE = """
void loadBinary(BitBuffer& buffer) {{
{load}}}"""

LOAD_INTEGER_TEMPLATE = """{member} = buffer.getInt();"""
LOAD_STRING_TEMPLATE = """{member} = buffer.getString();"""
LOAD_FLOAT_TEMPLATE = """{member} = buffer.getFloat();"""
LOAD_BOOLEAN_TEMPLATE = """{member} = buffer.getBit();"""
LOAD_LIST_TEMPLATE = """uint32_t {member}Count = buffer.getInt();
for (uint32_t i = 0; i < {member}Count; i++) {{
{submember_load}}}"""
LOAD_ENUM_TEMPLATE = """{member} = ({type}) buffer.getEnum((uint32_t) {type}Count);"""
LOAD_CLASS_TEMPLATE = """{member}.loadBinary(buffer);"""

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

    def check_unchanged(self, directory):
        filename = self._name + '.h'
        return common.check_cstyle_hash_comment(directory, filename, self._template_hash)

    def save_enum_at(self, directory):
        hpp = common.create_base_file(directory, self._name, '.h', self._data.get('comment'), self._template_hash)
        namespace = self._data.get('namespace')

        values_str = ''
        for i, val in enumerate(self._data['values']):
            values_str += val
            if i != len(self._data['values']) - 1:
                values_str += ',\n'

        values_str = common.incr_indent(values_str)

        enum_str = ENUM_TEMPLATE.format(name=self._name, values=values_str, count=len(self._data['values']))
        enum_str = common.incr_indent(enum_str)

        self.write_file_start(hpp, namespace)
        hpp.write('#include <cstddef>\n\n') # include definition of size_t
        hpp.write('namespace ' + namespace + ' {\n')
        hpp.write(enum_str)
        self.write_file_end(hpp, namespace)

        hpp.close()

    def save_class_at(self, directory):
        hpp = common.create_base_file(directory, self._name, '.h', self._data.get('comment'), self._template_hash)
        namespace = self._data.get('namespace')

        members_str = ''
        for i, member in enumerate(self._data['members']):
            type_str = common.get_real_type(member['type'], TYPE_MAP)

            m = type_str + ' m_' + member['name']
            if 'default' in member and not common.is_list(member['type']) and not common.is_class(member['type'], self._all_templates):
                m += ' = ' + member['default']
            m += ';'
            if i != len(self._data['members']) - 1:
                m += '\n'
            
            members_str += m

        members_str = common.incr_indent(members_str)

        generate_serialization = self._data.get('generate_serialization')
        serialization_str = '' if not generate_serialization else self.get_serialization_str()
        
        parent = self._data.get('parent')
        parent_str = '' if not parent else ' : public ' + parent
        class_str = CLASS_TEMPLATE.format(name=self._name, members=members_str, serialization=serialization_str, parent=parent_str)
        class_str = common.incr_indent(class_str)

        includes_str = ''
        if common.RecordType.LIST in self._used_builtins:
            includes_str += '#include <vector>\n'
        if common.RecordType.STRING in self._used_builtins:
            includes_str += '#include <string>\n'
        if common.RecordType.INTEGER in self._used_builtins:
            includes_str += '#include <cstdint>\n'
        if parent:
            includes_str += '#include "' + parent + '.h"\n'
        for used_custom in self._used_custom:
            if used_custom != self._name and used_custom != parent:
                includes_str += '#include "' + used_custom + '.h"\n'
        if generate_serialization:
            includes_str += '#include "BitBuffer.h"\n'
        if includes_str:
            includes_str += '\n'

        self.write_file_start(hpp, namespace)
        hpp.write(includes_str)
        hpp.write('namespace ' + namespace + ' {\n')
        hpp.write(class_str)
        self.write_file_end(hpp, namespace)
        
        hpp.close()

    def get_serialization_str(self):
        serialization_str = ''
        set_str = ''
        save_str = ''
        load_str = ''
        
        for i, member in enumerate(self._data['members']):
            set_str += self.get_member_set_str('m_' + member['name'], 'other.m_' + member['name'], member['type'])
            save_str += self.get_member_save_str('m_' + member['name'], member['type'])
            load_str += self.get_member_load_str('m_' + member['name'], member['type'])
            
            if i != len(self._data['members']) - 1:
                set_str += '\n'
                save_str += '\n'
                load_str += '\n'
        
        set_str = common.incr_indent(set_str)
        save_str = common.incr_indent(save_str)
        load_str = common.incr_indent(load_str)
        
        serialization_str += SET_TEMPLATE.format(type=self._name, set=set_str) + '\n'
        serialization_str += SAVE_TEMPLATE.format(save=save_str) + '\n'
        serialization_str += LOAD_TEMPLATE.format(load=load_str)
        serialization_str = common.incr_indent(serialization_str)
        
        return serialization_str
        
    def get_member_set_str(self, name, source_name, type):
        set_str = ''
        
        if common.is_list(type):
            list_type = common.get_list_type(type)
            real_list_type = common.get_real_type(list_type, TYPE_MAP)
            submember_set = real_list_type + ' item;\n'
            submember_set += self.get_member_set_str('item', 'otherItem', list_type) + '\n'
            submember_set += name + '.push_back(item);'
            submember_set = common.incr_indent(submember_set)
            set_str += SET_LIST_TEMPLATE.format(member=name, subtype=real_list_type, submember_set=submember_set)
        elif common.is_class(type, self._all_templates):
            set_str += name + '.set(' + source_name + ');'
        else:
            set_str += name + " = " + source_name + ';'

        return set_str

    def get_member_save_str(self, name, type):
        save_str = ''
        
        if type == common.RecordType.INTEGER:
            save_str += SAVE_INTEGER_TEMPLATE.format(member=name)
        elif type == common.RecordType.STRING:
            save_str += SAVE_STRING_TEMPLATE.format(member=name)
        elif type == common.RecordType.FLOAT:
            save_str += SAVE_FLOAT_TEMPLATE.format(member=name)
        elif type == common.RecordType.BOOLEAN:
            save_str += SAVE_BOOLEAN_TEMPLATE.format(member=name)
        elif common.is_list(type):
            list_type = common.get_list_type(type)
            real_list_type = common.get_real_type(list_type, TYPE_MAP)
            submember_save = self.get_member_save_str('item', list_type)
            submember_save = common.incr_indent(submember_save)
            save_str += SAVE_LIST_TEMPLATE.format(member=name, subtype=real_list_type, submember_save=submember_save)
        elif type in self._all_templates:
            if self._all_templates[type].data['type'] == common.ENUM_RECORD:
                save_str += SAVE_ENUM_TEMPLATE.format(member=name, type=type)
            else:
                save_str += SAVE_CLASS_TEMPLATE.format(member=name)

        return save_str

    def get_member_load_str(self, name, type):
        load_str = ''
        
        if type == common.RecordType.INTEGER:
            load_str += LOAD_INTEGER_TEMPLATE.format(member=name)
        elif type == common.RecordType.STRING:
            load_str += LOAD_STRING_TEMPLATE.format(member=name)
        elif type == common.RecordType.FLOAT:
            load_str += LOAD_FLOAT_TEMPLATE.format(member=name)
        elif type == common.RecordType.BOOLEAN:
            load_str += LOAD_BOOLEAN_TEMPLATE.format(member=name)
        elif common.is_list(type):
            list_type = common.get_list_type(type)
            real_list_type = common.get_real_type(list_type, TYPE_MAP)
            submember_load = real_list_type + ' item;\n'
            submember_load += self.get_member_load_str('item', list_type) + '\n'
            submember_load += name + '.push_back(item);'
            submember_load = common.incr_indent(submember_load)
            load_str += LOAD_LIST_TEMPLATE.format(member=name, submember_load=submember_load)
        elif type in self._all_templates:
            if self._all_templates[type].data['type'] == common.ENUM_RECORD:
                load_str += LOAD_ENUM_TEMPLATE.format(member=name, type=type)
            else:
                load_str += LOAD_CLASS_TEMPLATE.format(member=name)

        return load_str