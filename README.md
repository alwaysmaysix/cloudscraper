# SpankBang Downloader

[![PyPI version](https://badge.fury.io/py/cloudscraper.svg)](https://badge.fury.io/py/cloudscraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![image](https://img.shields.io/pypi/pyversions/cloudscraper.svg)](https://pypi.org/project/cloudscraper/)
[![Build Status](https://travis-ci.com/VeNoMouS/cloudscraper.svg?branch=master)](https://travis-ci.com/VeNoMouS/cloudscraper)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-brightgreen.svg)](https://www.buymeacoffee.com/venomous)



# Installation

Clone this repository and run `python setup.py install`.
Then `pip install bs4`
Then `pip install tqdm`

# Dependencies

- Python 3.x
- **[Requests](https://github.com/kennethreitz/requests)** >= 2.9.2
- **[requests_toolbelt](https://pypi.org/project/requests-toolbelt/)** >= 0.9.1

`python setup.py install` will install the Python dependencies automatically.

Any requests made from this session object to websites protected by Cloudflare anti-bot will be handled automatically. You can effectively treat SpankBang as if it is not protected with anything.

# Usage
1. Install Python 3
2. Clone this repository (download all files here)
3. Run setup.py
4. Take input.txt and sb_scraper.py do any directory you want and use it
5. Insert a .txt file as an argument in the command line (or drag a .txt file over the script file) into split.py to split it up into 4. You can run multiple instances of Scraper at once. 

# Features
- Drag a txt file of choice onto the .py file to run that, otherwise, double clicking will default to input.txt
- Playlist URLs as input work to output a .txt file of URLs which can then be fed back into the program
