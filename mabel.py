#! /usr/bin/env python3

import argparse
import generators
import os
import json
import template

def main():
    print()

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
        data = parse_template(f)
        name = os.path.splitext(os.path.basename(f))[0] # Removes '.json' from file
        templates[name] = template.Template(name, data)

    for lang in langs:
        if not lang['dir']:
            continue

        create_dir(lang['dir'])

        print('Generating ' + lang['name'] + ' files...')
        for t in templates.values():
            print('-> Processing: ' + t.name)
            
            generator_class = lang['generator']
            generator = generator_class()
            generator.set_values(t.name, t.data)
            generator.set_config(args, templates)
            path = lang['dir']
            if 'subdir' in t.data:
                path = os.path.join(path, t.data['subdir'])
                create_dir(path)
            generator.save_at(path)

        print('Done.\n')

def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def parse_template(path):
    with open(path) as f:
        return json.load(f)

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

    return parser.parse_args()

if __name__ == '__main__':
    main()