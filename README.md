# pymkup

pymkup is a Python library for viewing markups lists and property data in PDFs created by Bluebeam Revu.

## About

This is a reverse-engineered unofficial API for accessing data generated in Bluebeam Revu authored PDFs. Once a PDF is loaded, it can be scraped for some information. This is in very early development, and is being developed independently.

## Usage

```python
from pymkup import pymkup
x = pymkup("link to your pdf")

x.check_BB() # Checks if the document was authored by Revu
x.get_page_labels() # Returns page labels/"Page X" formats
x.get_markups_list() # A dump of all markups in a PDFDict object
x.get_markups_index() # A list of pages and markups by primary keys
x.markup_space() # A list of all markups by pk and a list of spaces associated
x.get_columns() # Returns master column/property fields list on all annotations
x.get_spaces() # A dump of all spaces in a PDFDict object
x.spaces_tree() # Generates a page label / spaces tree 3 levels (unfinished)
```

### Example output of spaces_tree() with test4.pdf
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

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
