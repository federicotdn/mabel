from . import generator
from . import common

ENUM_TEMPLATE = """public enum {name} {{
{values}}}
""" 

CLASS_TEMPLATE = """public class {name}{parent} {{
{members}{serialization}}}
"""

SERIALIZATION_TEMPLATE = """
public void SaveBinary(BitBuffer buffer) {{
{save}}}

public void LoadBinary(BitBuffer buffer) {{
{load}}}
"""

SAVE_INTEGER_TEMPLATE = """buffer.PutInt({member});"""
SAVE_STRING_TEMPLATE = """buffer.PutString({member});"""
SAVE_FLOAT_TEMPLATE = """buffer.PutFloat({member});"""
SAVE_BOOLEAN_TEMPLATE = """buffer.PutBit({member});"""
SAVE_LIST_TEMPLATE = """buffer.PutInt({member}.Count);
foreach ({subtype} item in {member}) {{
{submember_save}}}"""
SAVE_ENUM_TEMPLATE = """buffer.PutEnum({member});"""
SAVE_CLASS_TEMPLATE = """{member}.SaveBinary(buffer);"""

LOAD_INTEGER_TEMPLATE = """{member} = buffer.GetInt();"""
LOAD_STRING_TEMPLATE = """{member} = buffer.GetString();"""
LOAD_FLOAT_TEMPLATE = """{member} = buffer.GetFloat();"""
LOAD_BOOLEAN_TEMPLATE = """{member} = buffer.GetBit();"""
LOAD_LIST_TEMPLATE = """int {member}Count = buffer.GetInt();
for (int i = 0; i < {member}Count; i++) {{
{submember_load}}}"""
LOAD_ENUM_TEMPLATE = """{member} = buffer.GetEnum<{type}>();"""
LOAD_CLASS_TEMPLATE = """{member}.LoadBinary(buffer);"""

TYPE_MAP = {
    common.RecordType.INTEGER: 'int',
    common.RecordType.STRING: 'string',
    common.RecordType.FLOAT: 'float',
    common.RecordType.BOOLEAN: 'bool',
    common.RecordType.LIST: 'List'
}

class CsGenerator(generator.Generator):
    def check_unchanged(self, directory):
        filename = self._name + '.cs'
        return common.check_cstyle_hash_comment(directory, filename, self._template_hash)
    
    def save_enum_at(self, directory):
        cs = common.create_base_file(directory, self._name, '.cs', self._data.get('comment'), self._template_hash)
        namespace = self._data.get('namespace').title()

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
        cs = common.create_base_file(directory, self._name, '.cs', self._data.get('comment'), self._template_hash)
        namespace = self._data.get('namespace').title()

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

        generate_serialization = self._data.get('generate_serialization')
        serialization_str = '' if not generate_serialization else self.get_serialization_str()

        parent = self._data.get('parent')
        parent_str = '' if not parent else ' : ' + parent
        class_str = CLASS_TEMPLATE.format(name=self._name, members=members_str, serialization=serialization_str, parent=parent_str)
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

    def get_serialization_str(self):
        save_str = ''
        load_str = ''
        for i, member in enumerate(self._data['members']):
            save_str += self.get_member_save_str(member['name'], member['type'])
            load_str += self.get_member_load_str(member['name'], member['type'])
            
            if i != len(self._data['members']) - 1:
                save_str += '\n'
                load_str += '\n'
        
        save_str = common.incr_indent(save_str)
        load_str = common.incr_indent(load_str)
        
        serialization_str = SERIALIZATION_TEMPLATE.format(save=save_str, load=load_str)
        serialization_str = common.incr_indent(serialization_str)
        
        return serialization_str
        
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
            submember_load += name + '.Add(item);'
            submember_load = common.incr_indent(submember_load)
            load_str += LOAD_LIST_TEMPLATE.format(member=name, submember_load=submember_load)
        elif type in self._all_templates:
            if self._all_templates[type].data['type'] == common.ENUM_RECORD:
                load_str += LOAD_ENUM_TEMPLATE.format(member=name, type=type)
            else:
                load_str += LOAD_CLASS_TEMPLATE.format(member=name)

        return load_str