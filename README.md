# Lake Weed

![Python application](https://github.com/tac0x2a/lake_weed/workflows/Python%20application/badge.svg)

![Lake Weed](./doc/img/lakeweed_s.png)

Lake Weed is elastic converter for JSON, JSON Lines, and CSV string to use for constructin RDB query.
You can get schema and convertion values just input src string.

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
#   'date__as_datetime',
#   'date__as_string',
#   'str'
# )

print(types)
# (
#   'Array(Float64)',
#   'Array(String)',
#   'Array(String)',
#   'Array(String)',
#   'Array(DateTime64(6))',
#   'DateTime64(6)',
#   'String',
#   'String'
# )

print(values)
# [(
#   [1.0, 2.0, 3.0],
#   ['[1.1, 2.2]', '[3.3, 4.4]'],
#   ['[1, 2]', '[3, 4]'],
#   ['{"v": 1}', '{"v": 2}'],
#   [
#     datetime.datetime(2019, 9, 15, 14, 50, 3, 101000, tzinfo=tzoffset(None, 32400)),
#     datetime.datetime(2019, 9, 15, 14, 50, 3, 202000, tzinfo=tzoffset(None, 32400))
#   ],
#   datetime.datetime(2019, 9, 15, 14, 50, 3, 42042, tzinfo=tzoffset(None, 32400)),
#   '2019/09/15 14:50:03.042042043 +0900',
#   'Hello, LakeWeed'
# )]
```

## Example(CSV test to ClickHouse)
```py

src_csv = """
f,b,d
42,true,2019/09/15 14:50:03.101 +0900
"42","true",2019/12/15 14:50:03.101 +0900
"""

(columns, types, values) = clickhouse.data_string2type_value(src_csv)

print(columns)
# ('f', 'b', 'd', 'd_ns')

print(types)
# ('Float64', 'UInt8', 'DateTime64(6)')

print(values)
# [
#   (42.0, 1, datetime.datetime(2019, 9, 15, 14, 50, 3, 101000, tzinfo=tzoffset(None, 32400))),
#   (42.0, 1, datetime.datetime(2019, 12, 15, 14, 50, 3, 101000, tzinfo=tzoffset(None, 32400)))
# ]
```

## Example(Json lines test to ClickHouse)
Lake Weed converts each row of JSON in the same way as a single line of json.
Automatically selects the type so that all data can be stored. For example, if you have a mix of Numbers and Strings, select a String type that can store both.

```py

src_json_lines = """
{"f": 42,   "b": true,   "d": "2019/09/15 14:50:03.101 +0900"}
{"f": "42", "b": "true", "d": "2019/12/15 14:50:03.101 +0900"}
"""

(columns, types, values) = clickhouse.data_string2type_value(src_json_lines)


print(columns)
# ('f', 'b', 'd', 'd_ns')

print(types)
# ('String', 'String', 'DateTime64(6)')

# ('String', 'String', 'DateTime', 'UInt32')

print(values)
# [
#   ('42', 'true', datetime.datetime(2019, 9, 15, 14, 50, 3, 101000, tzinfo=tzoffset(None, 32400))),
#   ('42', 'true', datetime.datetime(2019, 12, 15, 14, 50, 3, 101000, tzinfo=tzoffset(None, 32400)))
# ]
```


## TypeMap
### Clickhouse

+ `Float`, `Double` : `Float64`
+ `Int`, `Integer` : `Int64`
+ `Bool`, `Boolean` : `UInt8` (True: 1, False: 0)
+ `String`, `Str` : `String`
+ `DateTime` : `DateTime64(6)` Nano seconds order is ignored.
+ `Array(Float)`, `Array(Double)` : `Array(Float64)`
+ `Array(Int)`, `Array(Integer)` : `Array(Int64)`
+ `Array(Bool)`, `Array(Boolean)` : `Array(UInt8)`
+ `Array(String)`,`Array(Str)`  : `Array(String)`
+ `Array(DateTime)` : `Array(DateTime64(6))`

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
