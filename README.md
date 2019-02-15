# qilib

Utility classes for Quantum Inspire.

# Installation

Install with pip:
```
$ python3 -m venv env
$ . ./env/bin/activate
(env) $ pip install .
```

# Testing

Run all unittests and collect the code coverage:
```
(env) $ coverage run --source="./src/qilib" -m unittest discover -s src/tests -t src -v
(env) $ coverage report -m
```
