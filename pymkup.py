import sys
import os
import pdfrw
from pdfrw.findobjs import find_objects
from pdfrw import PdfReader
from treelib import Node, Tree
from pathlib import Path


class pymkup:
    def __init__(self, file):
        self.file = file
        self.inpfn = os.path.dirname(os.path.realpath(__file__)) + self.file
        self.template_pdf = PdfReader(self.inpfn)
        self.file_name = Path(self.inpfn).stem

    # Checking if the PDF was authored by BB
    def check_BB(self):
        return True if ("Bluebeam" in self.template_pdf.Info.Creator) else False

    # Extract the page labels into a dictionary
    def get_page_labels(self):
        page_label_dict = {}
        try:
            page_labels = self.template_pdf.Root.PageLabels.Nums
            page_count = 0
            for i in range(1, len(page_labels), 2):
                try:
                    page_label_dict[page_count] = page_labels[i].P[1:-1]
                    page_count += 1
                except:
                    page_label_dict[page_count] = str(idx)
                    page_count += 1
        except:
            for idx, page in enumerate(self.template_pdf.pages):
                page_label_dict[idx] = str(idx+1)
        return(page_label_dict)

    # Extracting the entire markups list
    def get_markups_list(self):
        markups_list = {}
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for num, annotation in enumerate(page.Annots):
                    markups_list[num] = annotation
            except:
                pass
        return(markups_list)

    # Indexing the markups to their respective pages by PK
    def get_markups_index(self):
        markups_index = {}
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for num, annotation in enumerate(page.Annots):
                    markups_index[annotation.NM[1:-1]] = idx
            except:
                pass
        return(markups_index)

    # Extracting the current document's column/property lists
    # I probably missed some various properties.
    def get_columns(self):
        columns_lookup = {}
        # These are the default columns
        columns_lookup['/Subj'] = "Subject"
        columns_lookup['/CreationDate'] = "Creation Date"
        columns_lookup['/Label'] = "Label"
        columns_lookup['/T'] = 'Author'
        # Optional Content Group as "Name" key
        columns_lookup['/OC'] = "Layers"
        columns_lookup['/M'] = "Date"  # Technically "modified" date

        # These are hidden properties
        columns_lookup['/NM'] = "NM"  # Primary Key for Markup
        # Groupings by primary key and subject (>1)
        columns_lookup['/GroupNesting'] = 'Group Nesting'
        columns_lookup['/Type'] = 'Type'  # Annotation (markup) or otherwise
        columns_lookup['/Subtype'] = 'Subtype'  # Shape parent catagory
        columns_lookup['/CountStyle'] = 'Count Style'  # Count tool shape style
        # Exact layout of the markup in x,y coordinates
        columns_lookup['/Vertices'] = 'Vertices'
        columns_lookup['/BS'] = 'BS'  # Markup style
        columns_lookup['/Rect'] = 'Rectangle'  # Rectanular Coordinates
        # The count of the larger group where the markup is nested
        columns_lookup['/NumCounts'] = "NumCounts"
        columns_lookup['/IT'] = "IT"  # Type of counting (measurement)
        columns_lookup['/Contents'] = "Contents"  # Hex text comment

        # Properties
        # Scale where the markup falls and the multiplier
        columns_lookup['/BBMeasure'] = "BBMeasure"
        # Measurement Properties
        columns_lookup['/MeasurementTypes'] = 'Measurement Types'
        columns_lookup['/Measure'] = 'Measure'  # Measurement Properties
        columns_lookup['/RC'] = "Rich Text"  # Segment Rich Text Appearance
        columns_lookup['/CA'] = "CA"  # Opacity Property
        columns_lookup['/CountScale'] = 'Scale'  # Scale Property
        # Custom columns options and selections
        columns_lookup['/BSIColumnData'] = "BSI Column Data"
        columns_lookup['/DS'] = "DS"  # Caption font and style
        # Area Mesurement/Length Measurement
        columns_lookup['/SlopeType'] = 'Slope Type'
        # Related to pitch and run, slope properties
        columns_lookup['/PitchRun'] = 'PitchRun'
        columns_lookup['/DepthUnit'] = "Depth"
        # Start/End Line Cap in Length Measurement
        columns_lookup['/LE'] = 'Length Caps'
        # Line Width in Length Measurement
        columns_lookup['/LLE'] = 'Length Line Width'
        # The box where the entire line/lead is located
        columns_lookup['/L'] = 'Length Box'

        # These are hidden/unknown columns to me
        # Follows the markups (seconds in between marking up?)
        columns_lookup['/AP'] = 'AP'
        columns_lookup['/P'] = "P"  # All of the data combined
        # This may be if something is checked or not
        columns_lookup['/F'] = "F"
        # Unknown three option list, possibly status
        columns_lookup['/C'] = "C"
        # Mirrors C but returns empty list instead of blank with text
        columns_lookup['/IC'] = "IC"
        columns_lookup['/Version'] = "Version"  # Versioning, not sure how
        columns_lookup['/LL'] = 'LL'  # Another Length Property
        # T/F - may be related to measurement or not
        columns_lookup['/Cap'] = 'Cap'

        # Taking the current column list across pages in the file and putting it into in a dictionary
        column_list = []
        for page in range(0, len(self.template_pdf.pages)):
            for columns in self.template_pdf.pages[page].Annots[0]:
                column_list.append(columns)

        # Remove dupes
        [i for n, i in enumerate(column_list) if i not in column_list[:n]]

        # Create dictionary with original name and corrected names
        column_dict = {}
        for column in column_list:
            column_dict[column] = columns_lookup[column]

        return(column_dict)

    # /MeasurementTypes conversion to something more meaningful
    def measurement_types_convert(type_num):
        measurement_types = {}
        measurement_types[128] = "count"
        measurement_types[129] = "shape"
        measurement_types[130] = "length"
        measurement_types[132] = "volume"
        measurement_types[384] = "diameter"
        measurement_types[1152] = "angle"
        return(measurement_types)

    # /Contents conversion into something more meaningful
    def content_hex_convert(content):
        try:
            if ("feff" in content):
                content = str(content[5:-1])
                # remove breaks
                content = content.replace("000d00", "002000")
                return(bytes.fromhex(content).decode('utf-8'))
        except:
            return(content)

    def get_spaces(self):
        space_dict = {}
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for space in page.BSISpaces:
                    space_dict[idx] = space
            except:
                pass
        return(space_dict)

    def spaces_tree(self):
        spaces = self.get_spaces()
        page_labels = self.get_page_labels()
        spaces_tree = Tree()
        spaces_tree.create_node(self.file_name, self.file_name)

        # Add pages nodes
        for key, value in page_labels.items():
            spaces_tree.create_node(value, value, parent=self.file_name)

        # Add spaces nodes - top level only for now
        for space in spaces:
            spaces_tree.create_node(
                spaces[space].Title[1:-1], spaces[space].Title[1:-1] + str(space), parent=page_labels[space])

        return(spaces_tree)
