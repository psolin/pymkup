# pymkup

pymkup is a Python library for viewing markups lists and propery data in PDFs created by Bluebeam Revu.

## About

This is a reverse-engineered unofficial API for accessing data generated in Bluebeam Revu authored PDFs. Once a PDF is loaded, it can be scraped for some information. This is in very early development, and is being developed independently.

## Usage

```python
from pymkup import pymkup
x = pymkup("link to your pdf")

x.check_BB() # Sees if the document was authored by Revu
x.get_page_labels() # Returns all of the page labels and their sheet numbers
x.get_markups_list() # Returns all of the markups in
x.get_markups_index() # A list of pages / markup primary keys
x.get_columns() # Returns master column/property fields on all annotations
x.get_spaces() # Pulls a dictionary of all of the spaces in the document
x.spaces_tree() # creates a page label / spaces tree (unfinished)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
