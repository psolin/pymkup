# pymkup

pymkup is a Python library for viewing markups lists and property data in PDFs created by Bluebeam Revu.

## About

This is a reverse-engineered unofficial API for accessing data generated in Bluebeam Revu authored PDFs. Once a PDF is loaded, it can be scraped for some information. This is in very early development, and is being developed independently.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pymkup.

```bash
pip install pymkup
```

## Usage

```python
from pymkup import pymkup
x = pymkup("link to your pdf")

x.check_BB() # Checks if the document was authored by Revu
x.get_page_labels() # Returns page labels/"Page X" formats
x.markup_space() # A list of all spaces in a given markup.
x.get_columns() # Returns master column/property fields list on all annotations
x.spaces_hierarchy() # Generates a spaces tree.
x.spaces_hierarchy(output="dictionary") # Generates a spaces dictionary three levels deep.
x.spaces_hierarchy(output="hierarchy") # Generates a spaces hierarchy for use in the columns list.
x.data() # Returns JSON.
x.data(csv_file=True) # Generates a CSV with columns in default order.
```

### Data export with custom columns example

First, you should identify the columns that are accessible in your file:
```python
x.get_columns().values()
```

Second, you should review the extended columns here that can also be added:
```python
['Space', 'Page Number', 'Page Label', 'Measurement']
```

Lastly, you can build the custom columns that you want to see returned:
```python
columns = ['Subject', 'Label', 'Date', 'PK', 'Space']
x.data(column_list=columns)
```

### Example output of spaces tree ("test4.pdf")

```
test4
├── A101
│   ├── Level 1
│   │   └── Area A
│   │       ├── Room 101
│   │       ├── Room 102
│   │       └── Room 103
│   └── Sub Level
└── Page 2
    └── Level 1
        └── Area B
            ├── Room 151
            │   └── Sub-Room
            └── Room 152
```

## Requirements
- pdfrw is a library for scraping PDF data in Python and doing some other manipulaton. As of 2021, the author has not been updating it or allowing pull requests. This may change, but the library is still very functional.
- treelib is a library to create ASCII hierarchy trees in the spaces_tree() function.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
