from setuptools import setup

setup(name='qilib',
      description='',
      version='0.0.1',
      python_requires='>=3.6',
      package_dir={'': 'src'},
      packages=['qilib', 'qilib.data_set', 'qilib.utils'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'],
      license='Other/Proprietary License',
      install_requires=['pytest>=3.3.1', 'coverage>=4.5.1', 'numpy', 'serialize'])
