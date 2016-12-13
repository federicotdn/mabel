# mabel
A simple Python 3 tool that generates C#, C++ and Java POD objects from JSON files.

## Usage
```
usage: mabel.py [-h] [--cpp-path <path>] [--cs-path <path>]
                [--java-path <path>] [--force-gen]
                <JSON file> [<JSON file> ...]

Generate C#, C++ and Java POD objects or enums.

positional arguments:
  <JSON file>         JSON file to parse.

optional arguments:
  -h, --help          show this help message and exit
  --cpp-path <path>   Path used to store generated C++ files.
  --cs-path <path>    Path used to store generated C# files.
  --java-path <path>  Path used to store generated Java files.
  --force-gen         Force source file generation, even if templates have not
                      been modified.
```

## Examples
See the `examples` directory for examples.

## License
GPLv3 License.
