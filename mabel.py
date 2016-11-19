import argparse
import cpp_generator
import cs_generator
import java_generator
import common
import os

def main():
    parser = argparse.ArgumentParser(description='Generate C#, C++ and Java POD objects or enums.')
    args = parse_args(parser)

    langs = [
        {
            'name': 'C++',
            'dir': args.cpp_path,
            'generator': cpp_generator.CppGenerator
        },
        {
            'name': 'C#',
            'dir': args.cs_path,
            'generator': cs_generator.CsGenerator
        },
        {
            'name': 'Java',
            'dir': args.java_path,
            'generator': java_generator.JavaGenerator
        },
    ]

    for lang in langs:
        if not lang['dir']:
            continue

        create_dir(lang['dir'])
        
        print('Generating ' + lang['name'] + ' files...')
        for template in args.files:
            data = parse_template(template)
            name = os.path.splitext(os.path.basename(template))[0]

            print('-> Processing: ' + name)
            
            generator_class = lang['generator']
            generator = generator_class()
            generator.set_values(name, data)
            generator.set_config(args)
            generator.save_at(lang['dir'])

        print('Done.')

def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def parse_template(path):
    return common.json_from_path(path)

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