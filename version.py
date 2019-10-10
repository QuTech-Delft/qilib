from typing import Optional


def get_version_number(module: Optional[str] = 'qilib') -> str:
    """ Extract the version number from the source code.

    Pass the source module that contains the version.py file.
    This version number will be returned as a string.

    Args:
        module: module containing the version.py file

    Returns:
        the version number.
    """
    with open(f'src/{module}/version.py') as f:
        content = f.read()

    return content.split('\'')[1]


if __name__ == '__main__':
    print(get_version_number())
