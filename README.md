CAGR Explorer (CAGRex)
======================

Installation
------------
```bash
pip install git+https://github.com/caravelahc/cagrex
```

Usage
-----
```python
from cagrex import CAGR
from pprint import pprint


cagr = CAGR('id.ufsc', 'password')

pprint(cagr.user('18101234'))
pprint(cagr.course('GIT0101', '20181'))
```
