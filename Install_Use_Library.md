# dmtools_libraries

Short one-line description of what dmtools_libraries does.

[![PyPI](https://img.shields.io/pypi/v/mylib)](https://pypi.org/project/mylib/)
[![Python](https://img.shields.io/pypi/pyversions/mylib)](https://pypi.org/project/mylib/)
[![License](https://img.shields.io/pypi/l/mylib)](LICENSE)

## Installation

```bash
pip install dmtools_libraries
```

## Usage

```python
from dmtools_libraries import hello

print(hello())  # "hello"
```

## Development

Clone the repo and install in editable mode:

```bash
git clone https://github.com/YOURUSER/mylib.git
cd mylib
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Build the package locally and check it:

```bash
pip install build twine
python -m build
twine check dist/*
```

## Releasing

Publishing to PyPI is automated with GitHub Actions using
[trusted publishing](https://docs.pypi.org/trusted-publishers/), so no API token is stored.

1. Bump `version` in `pyproject.toml` and commit.
2. Create a GitHub release with a matching tag:
   ```bash
   gh release create v0.1.1 --generate-notes
   ```
3. The `Publish to PyPI` workflow builds the sdist and wheel and uploads them.

PyPI never allows a version number to be re-uploaded, so always bump the version for a new release.

## License

[MIT](LICENSE)
