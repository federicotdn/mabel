#! /usr/bin/env python3

import argparse
import generators
import os
import json
import template
import hashlib

def main():
    parser = argparse.ArgumentParser(description='Generate C#, C++ and Java POD objects or enums.')
    args = parse_args(parser)

    langs = [
        {
            'name': 'C++',
            'dir': args.cpp_path,
            'generator': generators.CppGenerator
        },
        {
            'name': 'C#',
            'dir': args.cs_path,
            'generator': generators.CsGenerator
        },
        {
            'name': 'Java',
            'dir': args.java_path,
            'generator': generators.JavaGenerator
        },
    ]
    
    templates = {}
    for f in args.files:
        try:
            data, template_hash = parse_template(f)
            name = os.path.splitext(os.path.basename(f))[0] # Removes '.json' from file
            templates[name] = template.Template(name, data, template_hash)
        except Exception as e:
            print('-> Error parsing json file ' + f + ': ' + str(e))

    skipped = 0
    created = 0

    for lang in langs:
        if not lang['dir']:
            continue

        create_dir(lang['dir'])

        print('Generating ' + lang['name'] + ' files...')
        for t in templates.values():
            print('-> Processing: ' + t.name)
            
            generator_class = lang['generator']
            generator = generator_class()
            generator.set_values(t.name, t.data, t.template_hash)
            generator.set_config(args, templates)
            path = lang['dir']
            if 'subdir' in t.data:
                path = os.path.join(path, t.data['subdir'])
                create_dir(path)
            
            written = generator.save_at(path)
            if not written:
                skipped += 1
                print('---> Skipped file (template unchanged).')
            else:
                created += 1

        print('Done ({lang}).\n'.format(lang=lang['name']))
    
    print('Processed {n} JSON template files.'.format(n=len(args.files)))
    print('Newly written source files: ', str(created))
    print('Skipped source files: ', str(skipped))

def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def parse_template(path):
    content = open(path).read()
    return json.loads(content), hashlib.md5(content.encode('utf8')).hexdigest()
    

def parse_args(parser):
    parser.add_argument('files', 
                        metavar='<JSON file>', 
                        type=str, 
                        help="JSON file to parse.",
                        nargs='+')

    parser.add_argument('--cpp-path',
                        metavar='<path>',
                        type=str,
                        default=None,
                        help='Path used to store generated C++ files.')

    parser.add_argument('--cs-path',
                        metavar='<path>',
                        type=str,
                        default=None,
                        help='Path used to store generated C# files.')

    parser.add_argument('--java-path',
                        metavar='<path>',
                        type=str,
                        default=None,
                        help='Path used to store generated Java files.')
                        
    parser.add_argument('--force-gen',
                        action='store_true',
                        help='Force source file generation, even if templates have not been modified.')                     

    return parser.parse_args()

if __name__ == '__main__':
    main()