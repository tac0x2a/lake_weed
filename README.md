# Lake Weed
[![Build Status](https://travis-ci.org/tac0x2a/lake_weed.svg?branch=master)](https://travis-ci.org/tac0x2a/lake_weed)

![Lake Weed](./doc/img/lakeweed_s.png)

Lake Weed is elastic converter JSON to RDB record.

# Install package
```
pip install lakeweed
```

PyPI: https://pypi.org/project/lakeweed/

# Release PyPI
## Create `~/.pypirc`
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

## Make Package
```sh
pip install wheel twine

rm -f -r lakeweed.egg-info/* dist/*
python setup.py sdist bdist_wheel
```

## Deploy to PyPI
```sh
# for testing
twine upload --repository testpypi dist/*
# open https://test.pypi.org/project/lakeweed/

# for production
twine upload --repository pypi dist/*
# open https://pypi.org/project/lakeweed/
```
