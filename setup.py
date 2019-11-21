"""Quantum Inspire library

Copyright 2019 QuTech Delft

qilib is available under the [MIT open-source license](https://opensource.org/licenses/MIT):

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from setuptools import setup


def get_version_number(module: str) -> str:
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


def get_long_description() -> str:
    """ Extract the long description from the README file."""
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

    return long_description


setup(name='qilib',
      description='Quantum Library for the Quantum Inspire platform',
      long_description=get_long_description(),
      long_description_content_type='text/markdown',
      version=get_version_number('qilib'),
      author='QuantumInspire',
      python_requires='>=3.6',
      package_dir={'': 'src'},
      packages=['qilib', 'qilib.configuration_helper', 'qilib.configuration_helper.adapters',
                'qilib.data_set', 'qilib.utils', 'qilib.utils.storage'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'],
      license='Other/Proprietary License',

      install_requires=['spirack>=0.1.8', 'numpy', 'serialize', 'zhinst', 'pymongo',
                        'requests', 'qcodes', 'qcodes_contrib_drivers', 'dataclasses-json'],
      extras_require={
          'dev': ['pytest>=3.3.1', 'coverage>=4.5.1', 'mongomock'],
      })
