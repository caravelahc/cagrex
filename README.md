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

pprint(cagr.user_classes('18101234'))
pprint(cagr.course_info('GIT0101', '20181'))
```
