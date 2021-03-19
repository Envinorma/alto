# Alto

[![Build Status](https://github.com/envinorma/alto/workflows/Build%20Main/badge.svg)](https://github.com/envinorma/alto/actions)
[![Documentation](https://github.com/envinorma/alto/workflows/Documentation/badge.svg)](https://envinorma.github.io/alto/)
[![Code Coverage](https://codecov.io/gh/envinorma/alto/branch/main/graph/badge.svg)](https://codecov.io/gh/envinorma/alto)

A Python parser for alto XML files, for handling OCR outputs

---

## Example usage

```python
from alto import parse_file

alto = parse_file('path/to/alto/file.xml')
print(alto.extract_words())
```

## Installation

**Stable Release:** `pip install alto_xml`<br>
**Development Head:** `pip install git+https://github.com/envinorma/alto.git`

## Documentation

For full package documentation please visit [envinorma.github.io/alto](https://envinorma.github.io/alto).

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to development.

**MIT license**
