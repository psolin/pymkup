import sys
import os
import pdfrw
from pdfrw.findobjs import find_objects
from pdfrw import PdfReader
from pathlib import Path
import csv
from time import mktime, strptime
from datetime import datetime
from fractions import Fraction
from columndata import *

class pymkup:
    def __init__(self, file):
        try:
            self.file = file
            self.inpfn = os.path.dirname(os.path.realpath(__file__)) + self.file
            self.template_pdf = PdfReader(self.inpfn)
            # Checking if the PDF was authored by BB
            bb_check = "Bluebeam" in self.template_pdf.Info.Creator
            self.file_name = Path(self.inpfn).stem
        except:
            pass

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

    # Indexing the markups to their respective pages by UUID
    def get_markups_index(self):
        markups_index = {}
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for num, annotation in enumerate(page.Annots):
                    markups_index[annotation.NM] = idx
            except:
                pass
        return(markups_index)

    # Runs through '/P' to get a Spaces list
    # Needs to be recoded entrirely per issue #18
    def markup_space(self, markup, spaces_list=[]):
        try:
            if markup['/P']:
                spaces_list = self.markup_space(markup.P.BSISpaces[0], spaces_list + [markup.P.BSISpaces[0].Title[1:-1]]);
            else: spaces_list = self.markup_space(markup.Kids[0], spaces_list + [markup.Kids[0].Title[1:-1]]);
        except:
            pass

        return(spaces_list)


    # Extracting the current document's column/property lists
    def get_columns(self):
        columns_lookup = column_data        

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

    # Dump of all spaces in each page
    def get_all_spaces(self):
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

    # Iterates through the spaces dictionary
    def spacesdict(self, spaces, prevparent):
        for item in spaces:
            try:
                prevparent[item.Title[1:-1]] = {}
                prevparent[item.Title[1:-1]] = self.spacesdict(item.Kids, {})
            except:
                pass

        return prevparent

    def spaces(self, output="dictionary"):
        spaces = self.get_all_spaces()
        page_labels = self.get_page_labels()
        data = {'spaces' : []}

        for key, value in page_labels.items():
            data['spaces'].append(self.spacesdict(spaces[key], {}))

        return data

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

    def measurement_col(self, markup):
        measurements = []
        if("sf" in str(self.content_hex_convert(markup['/Contents']))):
            sf_measure = self.content_hex_convert(markup['/Contents']).split(' ')
            measurements.append(sf_measure[0], sf_measure[1])
        elif(markup['/IT'] == "/PolygonCount"):
            measurements.append([1, "ct"])
        elif(markup['/IT'] in lf_columns):
            measurements.append([
                self.feet_inches_convert(self.content_hex_convert(markup['/Contents'])),
                'lf'])
        elif(markup['/IT'] == '/PolygonRadius'):
            r_measure = self.content_hex_convert(markup['/Contents'])
            measurements.append([
                self.feet_inches_convert(r_measure),
                'r ft'])
        elif(markup['/IT'] == '/PolygonVolume'):
            sf_measure = self.content_hex_convert(markup['/Contents']).split(" ", 1)
            measurements.append([sf_measure[0], sf_measure[1]])
        elif(markup['/IT'] == '/PolyLineAngle'):
            measurements.append([
                self.content_hex_convert(markup['/Contents']),
                '∠'])
        else:
            pass
        return(measurements[0])

    def space_markup(self, markup):
        space = self.markup_space(markup)
        
        if space is not None:
            if len(space) > 1:
                return('-'.join(space))
            else:
                return(space[0])

    def markups(self, column_list="default"):
        all_columns = self.get_columns()

        #Get out of there if no markups
        if(len(all_columns) == 0):
            return()

        if column_list == "default":
            chosen_columns = default_columns
        else:
            chosen_columns = {}
            for item in column_list:
                for idx in all_columns:
                    if(all_columns[idx] == item):
                        chosen_columns[idx] = item
                    #Adds the custom column where I can generate info
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
                column in custom_columns):
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
                    elif(column in first_slice):
                        row_dict[chosen_columns[column]] = markup[column][1:]
                    elif(column in no_mod):
                        row_dict[chosen_columns[column]] = markup[column]
                    elif(column == '/DepthUnit'):
                        row_dict[chosen_columns[column]] = markup[column][0]
                    elif(column == '/Contents'):
                        row_dict[chosen_columns[column]] = self.content_hex_convert(markup[column])
                    elif(column == '/AP'):
                        row_dict[chosen_columns[column]] = markup[column].N
                    elif(column in pdf_dates):
                        datestring = markup[column][3:-8]
                        ts = strptime(datestring, "%Y%m%d%H%M%S")
                        dt = datetime.fromtimestamp(mktime(ts))
                        row_dict[chosen_columns[column]] = dt
                    elif(column == '/MeasurementTypes'):
                        row_dict[chosen_columns[column]] = measurement_types[markup[column]]
                    #Handles imperial only for now
                    elif(column == 'Measurement'):
                        measurements = self.measurement_col(markup)
                        row_dict['Measurement'] = measurements[0]
                        row_dict['Type'] = measurements[1]
                    elif(column == "Type"):
                        pass
                    # Disabling spaces until it is fixed.
                    #elif("Space" in column): 
                        #row_dict['Space'] = self.space_markup(markup)
                    elif(markup[column] is not None):
                        row_dict[chosen_columns[column]] = markup[column][1:-1]
                    else:
                        pass
                else:
                    pass
            if(len(row_dict)>0):
                data['markups'].append(row_dict)
        return(data)