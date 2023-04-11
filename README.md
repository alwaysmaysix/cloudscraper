# cloudscraper

[![PyPI version](https://badge.fury.io/py/cloudscraper.svg)](https://badge.fury.io/py/cloudscraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![image](https://img.shields.io/pypi/pyversions/cloudscraper.svg)](https://pypi.org/project/cloudscraper/)
[![Build Status](https://travis-ci.com/VeNoMouS/cloudscraper.svg?branch=master)](https://travis-ci.com/VeNoMouS/cloudscraper)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-brightgreen.svg)](https://www.buymeacoffee.com/venomous)



# Installation

Alternatively, clone this repository and run `python setup.py install`.

# Dependencies

- Python 3.x
- **[Requests](https://github.com/kennethreitz/requests)** >= 2.9.2
- **[requests_toolbelt](https://pypi.org/project/requests-toolbelt/)** >= 0.9.1

`python setup.py install` will install the Python dependencies automatically. The javascript interpreters and/or engines you decide to use are the only things you need to install yourself, excluding js2py which is part of the requirements as the default.

Any requests made from this session object to websites protected by Cloudflare anti-bot will be handled automatically. You can effectively treat SpankBang as if it is not protected with anything.
