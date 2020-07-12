# Lake Weed
[![Build Status](https://travis-ci.org/tac0x2a/lake_weed.svg?branch=master)](https://travis-ci.org/tac0x2a/lake_weed)

![Lake Weed](./doc/img/lakeweed_s.png)

Lake Weed is elastic parser for data-like string, JSON, JSON Lines, and CSV to use for constructin RDB query.

# Usage
## Install package
```
pip install lakeweed
```

PyPI: https://pypi.org/project/lakeweed/

## Example(Json test to ClickHouse)
```py
from lakeweed import clickhouse

src_json = """
{
  "array" : [1,2,3],
  "array_in_array" : [[1.1, 2.2], [3.3, 4.4]],
  "nested_map" : {"value" : [[1,2], [3,4]]},
  "map_in_array"  : [{"v":1}, {"v":2}],
  "dates" : ["2019/09/15 14:50:03.101 +0900", "2019/09/15 14:50:03.202 +0900"],
  "date"  : {
    "as_datetime": "2019/09/15 14:50:03.042042043 +0900",
    "as_string"  : "2019/09/15 14:50:03.042042043 +0900"
  },
  "str"   : "Hello, LakeWeed"
}
"""

# Value types are guessed by lakeweed automatically.
# You can use specified type if you want.
my_types = {
    "date__as_string": "str"
}

(columns, types, values) = clickhouse.data_string2type_value(src_json, specified_types=my_types)

print(columns)
# (
#   'array',
#   'array_in_array',
#   'nested_map__value',
#   'map_in_array',
#   'dates',
#   'dates_ns',
#   'date__as_datetime',
#   'date__as_datetime_ns',
#   'date__as_string',
#   'str'
# )

print(types)
# (
#   'Array(Float64)',
#   'Array(String)',
#   'Array(String)',
#   'Array(String)',
#   'Array(DateTime)',
#   'Array(UInt32)',
#   'DateTime',
#   'UInt32',
#   'String',
#   'String'
# )

print(values)
# [(
#   [1, 2, 3],
#   ['[1.1, 2.2]', '[3.3, 4.4]'],
#   ['[1, 2]', '[3, 4]'],
#   ['{"v": 1}', '{"v": 2}'],
#   [
#     datetime.datetime(2019, 9, 15, 14, 50, 3, 101000, tzinfo=tzoffset(None, 32400)),
#     datetime.datetime(2019, 9, 15, 14, 50, 3, 202000, tzinfo=tzoffset(None, 32400))
#   ],
#   [101000000, 202000000],
#   datetime.datetime(2019, 9, 15, 14, 50, 3, 42042, tzinfo=tzoffset(None, 32400)),
#   42042043,
#   '2019/09/15 14:50:03.042042043 +0900',
#   'Hello, LakeWeed'
# )]

```


# Release PyPI

## Setup
### Create `~/.pypirc`
```ini
[distutils]
index-servers =
  pypi
  testpypi

[pypi]
repository: https://upload.pypi.org/legacy/
username: <Production Acciont Name>
password: <Password>

[testpypi]
repository: https://test.pypi.org/legacy/
username: <Testing Account Name>
password: <Password>
```

### Install packages for build and deploy
```sh
pip install wheel twine
```

## Build and Deploy
### Make Package
```sh
rm -f -r lakeweed.egg-info/* dist/*
python setup.py sdist bdist_wheel
```

### Local testing
```sh
python setup.py develop
```

### Deploy to PyPI
```sh
# for testing
twine upload --repository testpypi dist/*
# open https://test.pypi.org/project/lakeweed/

# for production
twine upload --repository pypi dist/*
# open https://pypi.org/project/lakeweed/
```

# Contributing
1. Fork it ( https://github.com/tac0x2a/lake_weed/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request