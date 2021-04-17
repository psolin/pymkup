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
from fractions import Fraction

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
    #This is broken for some files because of the hierarchy.
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
        try:
            if markup.P.BSISpaces:
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
        columns_lookup['/RiseDrop'] = 'Rise Drop'
        columns_lookup['/AlignOnSegment'] = 'Align On Segment'
        columns_lookup['/A'] = 'A'
        columns_lookup['/Border'] = 'Border'
        columns_lookup['/BSIBatchQuery'] = 'BSIBatchQuery'
        columns_lookup['/QuadPoints'] = 'QuadPoints'
        columns_lookup['/Dest'] = 'Dest'
        columns_lookup['/RD'] = 'RD'
        

        # Taking the current column list across pages in the file and putting it into in a dictionary
        column_list = []
        column_dict = {}
        for page in range(0, len(self.template_pdf.pages)):
            try:
                for columns in self.template_pdf.pages[page].Annots[0]:
                    column_list.append(columns)
            except:
                pass

        # Remove dupes
        [i for n, i in enumerate(column_list) if i not in column_list[:n]]

        # Create dictionary with original name and corrected names
        for column in column_list:
            column_dict[column] = columns_lookup[column]

        return(column_dict)

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
        if content == None:
            return(None)
        
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

    def spaces(self, output="tree"):
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

    def feet_inches_convert(self, text):
        feet, sep, inches = text.rpartition("\'")
        if(sep != "\'"):
            return('')
        inches = (inches[1:-1])
        feet = float(feet)
        if (' ') in inches:
            inches_whole, inches_fract = inches.split(' ')
            a = Fraction(inches_fract)
            inches = (float(a) + float(inches_whole))/12
        elif inches == 0:
            pass
        elif '/' in inches:
            a = Fraction(str(inches))
            inches = float(a)/12
        else:
            inches = float(inches)/12
        return(feet+inches)

    def markups(self, space_hierarchy=False, column_list="default"):
        all_columns = self.get_columns()

        #Get out of there if no markups
        if(len(all_columns) == 0):
            return()

        custom_columns = ['Measurement', 'Type', 'Page Label', 'Page Number']

        if column_list == "default":
            chosen_columns = {
            '/Subj': 'Subject', 
            'Page Label': 'Page Label',
            'Page Number' : 'Page Number',  
            '/Label': 'Label', 
            'Measurement' : 'Measurement',
            'Type' : 'Type',
            '/CreationDate': 'Creation Date',  
            '/T': 'Author', 
            '/M': 'Date', 
            '/Contents': 'Comments', 
            '/OC': 'Layer'}
            if(space_hierarchy == True):
               spaces_dump = self.spaces(output="hierarchy")
               for space in spaces_dump:
                    chosen_columns[space] = space
            else:
                chosen_columns['Space'] = 'Space'
        else:
            chosen_columns = {}
            for item in column_list:
                for idx in all_columns:
                    if(all_columns[idx] == item):
                        chosen_columns[idx] = item
                    #Adds the custom column where I can generate info
                    if(item == 'Space' and space_hierarchy == True):
                        spaces_dump = self.spaces(output="hierarchy")
                        for space in spaces_dump:
                            chosen_columns[space] = space
                    if(item == 'Measurement'):
                        chosen_columns['Measurement'] = 'Measurement'
                        chosen_columns['Type'] = 'Type'
                    elif(item not in all_columns.values()):
                        chosen_columns[item] = item

        chosen_columns_keys = list(chosen_columns.keys())

        data = {'markups' : []}

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

        #Pull the data out
        for markup in self.get_markups_list():
            #Fresh row
            row = []
            row_dict = {}
            for column in chosen_columns_keys:
                #Too much confusion.
                if markup['/Subj'] is None:
                    break
                elif((markup[column]) or 
                column in custom_columns or
                'Space' in column):
                    if(column == '/OC'):
                        row_dict[chosen_columns['/OC']] = markup['/OC'].Name[1:-1]
                    elif(column == '/IT'):
                        row_dict[chosen_columns[column]] = markup[column]
                    #Subject is needed to filter down results
                    elif(column == 'Page Number'):
                        row_dict[chosen_columns[column]] = markup_index[markup.NM]+1
                    elif(column == 'Page Label'):
                        if(markup_index[markup.NM] is not None):
                            row_dict['Page Label'] = page_label_index[markup_index[markup.NM]]
                    elif(
                        column == '/Type' or 
                        column == '/CountStyle' or 
                        column == '/Subtype'):
                        row_dict[chosen_columns[column]] = markup[column][1:]
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
                        row_dict[chosen_columns[column]] = markup[column]
                    elif(column == '/DepthUnit'):
                        row_dict[chosen_columns[column]] = markup[column][0]
                    elif(column == '/Contents'):
                        row_dict[chosen_columns[column]] = self.content_hex_convert(markup[column])
                    elif(column == '/AP'):
                        row_dict[chosen_columns[column]] = markup[column].N
                    elif(
                        column == '/CreationDate' or
                        column == '/M'):
                        datestring = markup[column][3:-8]
                        ts = strptime(datestring, "%Y%m%d%H%M%S")
                        dt = datetime.fromtimestamp(mktime(ts))
                        row_dict[chosen_columns[column]] = dt
                    elif(column == '/MeasurementTypes'):
                        row_dict[chosen_columns[column]] = self.measurement_types_convert(int(markup[column]))
                    #Handles imperial only for now
                    elif(column == 'Measurement'):
                        if("sf" in str(self.content_hex_convert(markup['/Contents']))):
                            sf_measure = self.content_hex_convert(markup['/Contents']).split(' ')
                            row_dict['Measurement'] = sf_measure[0]
                            row_dict['Type'] = sf_measure[1]
                        elif(markup['/IT'] == "/PolygonCount"):
                            row_dict['Measurement'] = 1
                            row_dict['Type'] = "ct"
                        elif(markup['/IT'] == "/PolyLineDimension" or
                            markup['/IT'] == "/LineDimension" or
                            markup['/IT'] == "/CircleDimension"):
                            row_dict['Measurement'] = self.feet_inches_convert(self.content_hex_convert(markup['/Contents']))
                            row_dict['Type'] = "lf"
                        elif(markup['/IT'] == '/PolygonRadius'):
                            r_measure = self.content_hex_convert(markup['/Contents'])
                            row_dict['Measurement'] = self.feet_inches_convert(r_measure)
                            row_dict['Type'] = 'r ft'
                        elif(markup['/IT'] == '/PolygonVolume'):
                            sf_measure = self.content_hex_convert(markup['/Contents']).split(" ", 1)
                            row_dict['Measurement'] = sf_measure[0]
                            row_dict['Type'] = sf_measure[1]
                        elif(markup['/IT'] == '/PolyLineAngle'):
                            row_dict['Measurement'] = self.content_hex_convert(markup['/Contents'])
                            row_dict['Type'] = '∠'
                    elif(column == "Type"):
                        pass
                    elif("Space" in column): 
                        space = self.markup_space(markup)
                        if space is not None:
                            if space_hierarchy == True:
                                if len(space) > 1:
                                    for k, v in spaces_dump.items():
                                        for s in space:
                                            if s in v:
                                                row_dict[k] = s
                            else:
                                row_dict[chosen_columns[column]] = '-'.join(space)
                    elif(markup[column] is not None):
                        row_dict[chosen_columns[column]] = markup[column][1:-1]
                    else:
                        pass
                else:
                    pass
            if(len(row_dict)>0):
                data['markups'].append(row_dict)
        return(data)