# mabel
Use `.json` files to create POD objects, or enums, for C#, C++ and Java.

## Usage
```
usage: mabel.py [-h] [--cpp-path <path>] [--cs-path <path>]
                [--java-path <path>]
                <JSON file> [<JSON file> ...]

Generate C#, C++ and Java POD objects or enums.

positional arguments:
  <JSON file>         JSON file to parse.

optional arguments:
  -h, --help          show this help message and exit
  --cpp-path <path>   Path used to store generated C++ files.
  --cs-path <path>    Path used to store generated C# files.
  --java-path <path>  Path used to store generated Java files.
```

## Examples
Creating an enum:

`Color.json`
```json
{
    "type": "enum",
    "namespace": "test",
    "values": ["RED", "BLUE", "GREEN", "YELLOW"]
}
```

Generated C++ header file:

`Color.h`
```C++
#ifndef TEST_TEST_H
#define TEST_TEST_H

namespace test {
	enum class Color {
		RED,
		BLUE,
		GREEN,
		YELLOW
	};
}

#endif //TEST_TEST_H
```

Creating a class/struct:

`Animal.json`
```json
{
    "type": "class",
    "namespace": "test",
    "parent": "Entity",
    "members": [
        {
            "name": "age",
            "type": "int"
        },
        {
            "name": "height",
            "type": "float"
        },
        {
            "name": "friends",
            "type": "list<Animal>"
        },
        {
            "name": "owner",
            "type": "string"
        }
    ]
}
```

Generated C++ header file:

`Animal.h`
```C++
#ifndef TEST_ANIMAL_H
#define TEST_ANIMAL_H

#include <vector>
#include <string>
#include "Entity.h"

namespace test {
	struct Animal : public Entity {
		uint32_t m_age;
		float m_height;
		std::vector<Animal> m_friends;
		std::string m_owner;
	};
}

#endif //TEST_ANIMAL_H
```

## License
GPLv3 License.