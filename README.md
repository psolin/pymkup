# pymkup

pymkup is a Python library for viewing markups lists and property data in PDFs created by Bluebeam Revu.

## About

This is a reverse-engineered unofficial API for accessing data generated in Bluebeam Revu authored PDFs. Once a file is loaded, it can be scraped for some information.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pymkup.

```bash
pip install pymkup
```

## Usage

```python
from pymkup import pymkup
x = pymkup("link to your Revu PDF")
x.spaces() # Returns JSON dictionary of document spaces.
x.markups() # Returns JSON dictionary of markups.
```

### Data export with custom columns example

First, you should identify the columns that are accessible in your file:
```python
x.get_columns().values()
```

Second, you should review the extended columns here that can also be added:
```python
['Page Number', 'Page Label', 'Measurement', 'Space']
```

Lastly, you can build the custom columns that you want to see returned:
```python
columns = ['Subject', 'Label', 'Date', 'UUID', 'Space']
x.markups(column_list=columns)
```

## Requirements
- pdfrw is a library for scraping PDF data in Python and doing some other manipulaton.
- shapely to build Spaces.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
