from . import generator
from . import common

ENUM_TEMPLATE = """public enum {name} {{
{values}}}
""" 

CLASS_TEMPLATE = """public class {name}{parent}{extends} {{
{members}{serialization}}}
"""

IMPORT_TEMPLATE="""import {path};\n"""

SET_TEMPLATE = """
public void set({type} other) {{
{set}}}"""

SET_LIST_TEMPLATE = """for ({subtype} otherItem : other.{member}) {{
{submember_set}}}"""

SAVE_TEMPLATE = """
public void saveBinary(BitBuffer buffer) {{
{save}}}"""

SAVE_INTEGER_TEMPLATE = """buffer.putInt({member});"""
SAVE_STRING_TEMPLATE = """buffer.putString({member});"""
SAVE_FLOAT_TEMPLATE = """buffer.putFloat({member});"""
SAVE_BOOLEAN_TEMPLATE = """buffer.putBit({member});"""
SAVE_LIST_TEMPLATE = """buffer.putInt({member}.size());
for ({subtype} item : {member}) {{
{submember_save}}}"""
SAVE_ENUM_TEMPLATE = """buffer.putEnum({member});"""
SAVE_CLASS_TEMPLATE = """{member}.saveBinary(buffer);"""

LOAD_TEMPLATE = """
public void loadBinary(BitBuffer buffer) {{
{load}}}"""

LOAD_INTEGER_TEMPLATE = """{member} = buffer.getInt();"""
LOAD_STRING_TEMPLATE = """{member} = buffer.getString();"""
LOAD_FLOAT_TEMPLATE = """{member} = buffer.getFloat();"""
LOAD_BOOLEAN_TEMPLATE = """{member} = buffer.getBit();"""
LOAD_LIST_TEMPLATE = """int {member}Count = buffer.getInt();
for (int i = 0; i < {member}Count; i++) {{
{submember_load}}}"""
LOAD_ENUM_TEMPLATE = """{member} = buffer.getEnum({type}.class);"""
LOAD_CLASS_TEMPLATE = """{member}.loadBinary(buffer);"""

TYPE_MAP = {
    common.RecordType.INTEGER: 'int',
    common.RecordType.STRING: 'String',
    common.RecordType.FLOAT: 'float',
    common.RecordType.BOOLEAN: 'boolean',
    common.RecordType.LIST: 'ArrayList'
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
            if common.is_list(member['type']) or common.is_class(member['type'], self._all_templates):
                m += ' = new ' + type_str + '()'
            elif 'default' in member:
                m += ' = ' + member['default']
            m += ';'
            if i != len(self._data['members']) - 1:
                m += '\n'
            
            members_str += m

        members_str = common.incr_indent(members_str)

        generate_serialization = self._data.get('generate_serialization')
        serialization_str = '' if not generate_serialization else self.get_serialization_str()

        parent = self._data.get('parent')
        parent_str = '' if not parent else ' extends ' + parent
        
        interface = self._data.get('implements')
        interface_str = '' if not interface else ' implements ' + interface
        
        class_str = CLASS_TEMPLATE.format(name=self._name, members=members_str, serialization=serialization_str, parent=parent_str, extends=interface_str)

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
        
        if generate_serialization:
            imports_str += 'import utils.phantom.multiplayer.BitBuffer;\n'
        
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
        
    def get_serialization_str(self):
        serialization_str = ''
        set_str = ''
        save_str = ''
        load_str = ''
        
        for i, member in enumerate(self._data['members']):
            set_str += self.get_member_set_str(member['name'], 'other.' + member['name'], member['type'])
            save_str += self.get_member_save_str(member['name'], member['type'])
            load_str += self.get_member_load_str(member['name'], member['type'])
            
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
            submember_set = real_list_type + ' item = new ' + real_list_type + '();\n'
            submember_set += self.get_member_set_str('item', 'otherItem', list_type) + '\n'
            submember_set += name + '.add(item);'
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
            submember_load = real_list_type + ' item = new ' + real_list_type + '();\n'
            submember_load += self.get_member_load_str('item', list_type) + '\n'
            submember_load += name + '.add(item);'
            submember_load = common.incr_indent(submember_load)
            load_str += LOAD_LIST_TEMPLATE.format(member=name, submember_load=submember_load)
        elif type in self._all_templates:
            if self._all_templates[type].data['type'] == common.ENUM_RECORD:
                load_str += LOAD_ENUM_TEMPLATE.format(member=name, type=type)
            else:
                load_str += LOAD_CLASS_TEMPLATE.format(member=name)

        return load_str