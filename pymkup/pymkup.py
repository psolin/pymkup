import sys
import os
import pdfrw
from pdfrw.findobjs import find_objects
from pdfrw import PdfReader
from treelib import Node, Tree
from pathlib import Path
import csv
from time import mktime, strptime
from datetime import datetime

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
        #This will work if there are any page labels
        try:
            page_num_list = self.template_pdf.Root.PageLabels.Nums
            for idx, page in enumerate(page_num_list[1::2]):
                try:
                    page_label_dict[idx] = page.P[1:-1]
                except:
                    page_label_dict[idx] = "Page " + str(idx + 1)
        #Otherwise, do a mass naming scheme
        except:
            for idx, page in enumerate(self.template_pdf.pages):
                page_label_dict[idx] = "Page " + str(idx + 1)

        return(page_label_dict)

    # Extracting the entire markups list
    def get_markups_list(self):
        markups_list = []
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for num, annotation in enumerate(page.Annots):
                    markups_list.append(annotation)
            except:
                pass
        return(markups_list)

    # Indexing the markups to their respective pages by PK
    def get_markups_index(self):
        markups_index = {}
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for num, annotation in enumerate(page.Annots):
                    markups_index[annotation.NM] = idx
            except:
                pass
        return(markups_index)

    def markup_space(self, markup):
        markup_spaces = {}
        spaces_list = []
        if markup.P.BSISpaces:
            try:
                #This is way too much. Can support spaces 6 deep...
                spaces_list.append(markup.P.BSISpaces[0].Title[1:-1])
                spaces_list.append(markup.P.BSISpaces[0].Kids[0].Title[1:-1])
                spaces_list.append(markup.P.BSISpaces[0].Kids[0].Kids[0].Title[1:-1])
                spaces_list.append(markup.P.BSISpaces[0].Kids[0].Kids[0].Kids[0].Title[1:-1])
                spaces_list.append(markup.P.BSISpaces[0].Kids[0].Kids[0].Kids[0].Kids[0].Title[1:-1])
                spaces_list.append(markup.P.BSISpaces[0].Kids[0].Kids[0].Kids[0].Kids[0].Kids[0].Title[1:-1])
            except:
                pass
        return(spaces_list)

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
        columns_lookup['/OC'] = "Layer"
        columns_lookup['/M'] = "Date"  # Technically "modified" date
        columns_lookup['/Contents'] = "Comments"  # Hex text comment

        # These are hidden properties
        columns_lookup['/NM'] = "PK"  # Primary Key for Markup
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

        # Properties
        # Scale where the markup falls and the multiplier
        columns_lookup['/BBMeasure'] = "BBMeasure"
        # Describes the XObjects
        columns_lookup['/AP'] = 'AP'
        # Measurement Properties
        columns_lookup['/MeasurementTypes'] = 'Measurement Types'
        columns_lookup['/Measure'] = 'Measure'  # Measurement Properties
        columns_lookup['/RC'] = "Rich Text"  # Segment Rich Text Appearance
        columns_lookup['/CA'] = "Opacity"  # Opacity Property
        columns_lookup['/CountScale'] = 'Scale'  # Scale Property
        # Custom columns options and selections
        columns_lookup['/BSIColumnData'] = "BSIColumnData"
        columns_lookup['/DS'] = "DS"  # Caption font and style
        # Area Mesurement/Length Measurement
        columns_lookup['/SlopeType'] = 'Slope Type'
        # Related to pitch and run, slope properties
        columns_lookup['/PitchRun'] = 'PitchRun'
        columns_lookup['/DepthUnit'] = "Depth Unit"
        columns_lookup['/Depth'] = "Depth"
        # Start/End Line Cap in Length Measurement
        columns_lookup['/LE'] = 'Length Caps'
        # Line Width in Length Measurement
        columns_lookup['/LLE'] = 'Length Line Width'
        # The box where the entire line/lead is located
        columns_lookup['/L'] = 'Length Box'

        # These are hidden/unknown columns to me
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
        column_dict = {}
        for page in range(0, len(self.template_pdf.pages)):
            try:
                for columns in self.template_pdf.pages[page].Annots[0]:
                    column_list.append(columns)
            except:
                return(column_dict)

        # Remove dupes
        [i for n, i in enumerate(column_list) if i not in column_list[:n]]

        # Create dictionary with original name and corrected names
        for column in column_list:
            column_dict[column] = columns_lookup[column]

        return(column_dict)

    #Converts /IT column
    def IT_convert(self, markup):
        IT_dict = {}
        IT_dict['/PolygonCount'] = "Polygon Count"
        IT_dict['/PolyLineDimension'] = "PolyLine Dimension"
        IT_dict['/LineDimension'] = "Line Dimension"
        return(IT_dict[markup])

    # /MeasurementTypes conversion to something more meaningful
    def measurement_types_convert(self, markup):
        measurement_types = {}
        measurement_types[128] = "Count"
        measurement_types[129] = "Shape"
        measurement_types[130] = "Length"
        measurement_types[132] = "Volume"
        measurement_types[384] = "Diameter"
        measurement_types[1152] = "Angle"
        return(measurement_types[markup])

    # /Contents conversion into something more meaningful
    def content_hex_convert(self, content):
        try:
            if ("feff" in content):
                content = content.decode_hex()
                content = content.decode('utf-16')
                content = content.splitlines()[1]
        except:
            pass

        #Remove the parenthesis
        if(content[0] == "("):
            content = content[1:-1]

        def RepresentsInt(s):
            try: 
                int(s)
                return True
            except ValueError:
                return False

        if(RepresentsInt(content) == True):
            content = ""

        return(content)


    def get_spaces(self):
        space_list = []
        space_dict = {}
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for space in page.BSISpaces:
                    space_list.append(space)
            except:
                pass
            space_dict[idx] = space_list
            space_list = []
        return(space_dict)

    def spaces_hierarchy(self, output="tree"):
        spaces = self.get_spaces()
        page_labels = self.get_page_labels()
        spaces_tree = Tree()
        #Add PDF name as top node
        spaces_tree.create_node(self.file_name, self.file_name)     

        #Add pages nodes
        for key, value in page_labels.items():
            spaces_tree.create_node(value, value, parent=self.file_name)

        for space in spaces:
            #This is way too much. Can support spaces 3 deep.

            #Level 1
            try:
                for item in spaces[space]:
                    pk = list[item.Title, space]
                    spaces_tree.create_node(
                            item.Title[1:-1], pk, parent=page_labels[space])
            except:
                pass

            try:
                for item in spaces[space][0].Kids:
                    pk = list[spaces[space][0].Title, space]
                    spaces_tree.create_node(
                        item.Title[1:-1], pk, parent=list[spaces[space][0].Title, space])
                    if item.Kids is not None:
                        for kid in item.Kids:
                            pk = list[spaces[space].Title, space]
                            spaces_tree.create_node(
                            kid.Title[1:-1], pk, parent=list[spaces[space][0].Title, space])
            except:
                pass

            #Level 2
            try:
                for item in spaces[space][0].Kids:
                    pk = list[item.Title, space]
                    spaces_tree.create_node(
                        item.Title[1:-1], pk, parent=list[spaces[space][0].Title, space])
                    if item.Kids is not None:
                        for kid in item.Kids:
                            pk = list[kid.Title, space]
                            spaces_tree.create_node(
                            kid.Title[1:-1], pk, parent=list[spaces[space][0].Spaces[0].Title, space])
            except:
                pass

            #Level 3
            try:
                for item in spaces[space][0].Kids[0].Kids:
                    pk = list[item.Title, space]
                    spaces_tree.create_node(
                        item.Title[1:-1], pk, parent=list[spaces[space][0].Kids[0].Title, space])
                    if item.Kids is not None:
                        for kid in item.Kids:
                            spaces_tree.create_node(
                            kid.Title[1:-1], pk, parent=list[spaces[space][0].Kids[0].Kids[0].Title, space])
            except:
                pass

        if output == "tree":
            return(spaces_tree)
        elif output == "hierarchy":
            #Getting a master space hierarchy by column
            #Max depth starts calculating outside the doc name and sheet name
            max_depth = max([len(i) for i in spaces_tree.paths_to_leaves()]) - 2
            space_depth = []
            for level in range(max_depth):
                space_depth.append("Space " + str(level + 1))
            
            #Create the dictionary to hold the values
            space_dict = {} 
            for idx, level in enumerate(space_depth):
                space_dict[level] = []
            
            #Loop through all space items
            for item in spaces_tree.paths_to_leaves():
                for level, space in enumerate(item[2:]):
                    res = list(space_dict.keys())[level]
                    if str(space)[7:-6] not in space_dict[res]:
                        space_dict[res].append(str(space)[7:-6])
            return(space_dict)
        elif output == "dictionary":
            # Return the Python dictionary
            return(spaces_tree.to_dict())

    def csv_export(self, column_list="default"):
        all_columns = self.get_columns()

        if column_list == "default":
            chosen_columns = {
            '/Subj': 'Subject', 
            'Page Label': 'Page Label', 
            '/Label': 'Label', 
            '/CreationDate': 'Creation Date',  
            '/T': 'Author', 
            '/M': 'Date', 
            '/Contents': 'Comments', 
            '/OC': 'Layer', 
            'Space': 'Space'}
        else:
            chosen_columns = {}
            for item in column_list:
                for idx in all_columns:
                    if(all_columns[idx] == item):
                        chosen_columns[idx] = item
                    #Adds the custom column where I can generate info
                    elif(item not in all_columns.values()):
                        chosen_columns[item] = item

        #Get out of there if no markups
        if(len(all_columns) == 0):
            return()

        chosen_columns_keys = list(chosen_columns.keys())

        #Handles Page Number
        try:
            if(chosen_columns['Page Number']):
                markup_index = self.get_markups_index()
        except:
            pass

        #Handles Page Label
        try:
            if(chosen_columns['Page Label']):
                markup_index = self.get_markups_index()
                page_label_index = self.get_page_labels()
        except:
            pass

        with open(self.file_name + '.csv', mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #Write the header row
            csv_writer.writerow(list(chosen_columns.values()))

            #Pull the data out
            for markup in self.get_markups_list():
                #Fresh row
                row = []
                for column in chosen_columns_keys:
                    try:
                        if(column == '/OC'):
                            row.append(markup[column].Name[1:-1])
                        elif(column == '/IT'):
                            row.append(self.IT_convert(markup[column]))
                        elif(column == 'Page Number'):
                            row.append(markup_index[markup.NM]+1)
                        elif(column == 'Page Label'):
                            row.append(page_label_index[markup_index[markup.NM]])
                        elif(
                            column == '/Type' or 
                            column == '/CountStyle' or 
                            column == '/Subtype'):
                            row.append(markup[column][1:])
                        elif(
                            column == '/NumCounts' or
                            column == '/Version' or
                            column == '/GroupNesting' or
                            column == '/Version' or
                            column == '/F' or
                            column == '/BS' or
                            column == '/IC' or
                            column == '/DS' or
                            column == '/BSIColumnData' or
                            column == '/Vertices' or
                            column == '/Rect' or
                            column == '/Version' or
                            column == '/BBMeasure' or
                            column == '/CA'):
                            row.append(markup[column])
                        elif(column == '/DepthUnit'):
                            row.append(markup[column][0])
                        elif(column == '/Contents'):
                            row.append(self.content_hex_convert(markup[column]))
                        elif(column == '/AP'):
                            row.append(markup[column].N)
                        elif(
                            column == '/CreationDate' or
                            column == '/M'):
                            datestring = markup[column][3:-8]
                            ts = strptime(datestring, "%Y%m%d%H%M%S")
                            dt = datetime.fromtimestamp(mktime(ts))
                            row.append(dt)
                        elif(column == '/MeasurementTypes'):
                            row.append(self.measurement_types_convert(int(markup[column])))
                        #This is not iterating correctly
                        elif(column == 'Space'): 
                            row.append('-'.join(self.markup_space(markup)))
                        else:
                            row.append(markup[column][1:-1])
                    except:
                        row.append("")
                csv_writer.writerow(row)

        return()