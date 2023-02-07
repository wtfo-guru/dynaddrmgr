# dynaddrmgr

[![Build Status](https://github.com/wtfo-guru/dynaddrmgr/actions/workflows/test.yml/badge.svg)](https://github.com/wtfo-guru/dynaddrmgr/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/wtfo-guru/dynaddrmgr/branch/main/graph/badge.svg)](https://codecov.io/gh/wtfo-guru/dynaddrmgr)
[![Python Version](https://img.shields.io/pypi/pyversions/dynaddrmgr.svg)](https://pypi.org/project/dynaddrmgr/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

Tools to manage actions based on dynamic host address changes.


## Features

- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)
- Manages content of files based on current ipaddress(es) of specified hostname(s), using jinja2 templates


## Installation

```bash
pip install dynaddrmgr
```


## Example

Showcase how your project can be used:

```python
from dynaddrmgr.example import some_function

print(some_function(3, 4))
# => 7
```

## License

[MIT](https://github.com/wtfo-guru/dynaddrmgr/blob/main/LICENSE)


## Credits

This project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [9899cb192f754a566da703614227e6d63227b933](https://github.com/wemake-services/wemake-python-package/tree/9899cb192f754a566da703614227e6d63227b933). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/9899cb192f754a566da703614227e6d63227b933...master) since then.
