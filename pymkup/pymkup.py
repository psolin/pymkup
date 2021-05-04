from pdfrw import PdfReader
from os.path import dirname, realpath
from pathlib import Path
from column_data import *
from data_conversion import *


class Pymkup:
    def __init__(self, file):
        try:
            self.file = file
            self.inpfn = dirname(realpath(__file__)) + self.file
            self.template_pdf = PdfReader(self.inpfn)

            # Checking if the PDF was authored by BB
            "Bluebeam" in self.template_pdf.Info.Creator
            self.file_name = Path(self.inpfn).stem
            self.spaces_path = {}
        except Exception:
            print(self.inpfn, "doesnt exist.")

    # Extract the page labels into a dictionary
    # This is broken for some files because of the hierarchy.
    def get_page_labels(self):
        page_label_dict = {}
        # This will work if there are any page labels
        try:
            page_num_list = self.template_pdf.Root.PageLabels.Nums
            for idx, page in enumerate(page_num_list[1::2]):
                try:
                    page_label_dict[idx] = page.P[1:-1]
                except Exception:
                    page_label_dict[idx] = "Page " + str(idx + 1)
        # Otherwise, do a mass naming scheme
        except Exception:
            for idx, page in enumerate(self.template_pdf.pages):
                page_label_dict[idx] = "Page " + str(idx + 1)

        return page_label_dict

    # Extracting the entire markups list
    def get_markups_list(self):
        markups_list = []
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for num, annotation in enumerate(page.Annots):
                    markups_list.append(annotation)
            except Exception:
                pass
        return markups_list

    # Indexing the markups to their respective pages by UUID
    def get_markups_index(self):
        markups_index = {}
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for num, annotation in enumerate(page.Annots):
                    markups_index[annotation.NM] = idx
            except Exception:
                pass
        return markups_index

    # Extracting the current document's column/property lists
    def get_columns(self):

        columns_lookup = column_data

        # Taking the current column list across pages in the file and putting
        # it into in a dictionary
        column_list = []
        column_dict = {}
        for page in range(0, len(self.template_pdf.pages)):
            try:
                for columns in self.template_pdf.pages[page].Annots[0]:
                    column_list.append(columns)
            except Exception:
                pass

        # Remove dupes
        [i for n, i in enumerate(column_list) if i not in column_list[:n]]

        # Create dictionary with original name and corrected names
        for column in column_list:
            column_dict[column] = columns_lookup[column]

        return column_dict

    # Dump of all spaces by page
    def get_all_spaces(self):
        space_list = []
        space_dict = {}
        for idx, page in enumerate(self.template_pdf.pages):
            try:
                for space in page.BSISpaces:
                    space_list.append(space)
            except Exception:
                pass
            space_dict[idx] = space_list
            space_list = []
        return space_dict

    # Iterates through the spaces dictionary
    def spacesdict(self, spaces, key, prevparent):
        for item in spaces:
            try:
                self.spaces_path[key].append({item.Title[1:-1]: item.Path})
                prevparent[item.Title[1:-1]] = {}
                prevparent[item.Title[1:-1]] \
                    = self.spacesdict(item.Kids, key, {})
            except Exception:
                pass

        return prevparent

    def spaces(self, output="dictionary"):
        spaces = self.get_all_spaces()
        if spaces is None:
            return {'spaces': []}

        page_labels = self.get_page_labels()
        data = {'spaces': []}

        for key, value in page_labels.items():
            self.spaces_path[key] = []
            data['spaces'].append(key)
            data['spaces'].append(self.spacesdict(spaces[key], key, {}))

        if output == 'dictionary':
            return data

        if output == 'vertices':
            return self.spaces_path

    def markups(self, column_list="default"):
        all_columns = self.get_columns()

        # Get out of there if no markups
        if len(all_columns) == 0:
            return {'markups': []}

        if column_list == "default":
            chosen_columns = default_columns
        else:
            chosen_columns = {}
            for item in column_list:
                for idx in all_columns:
                    if all_columns[idx] == item:
                        chosen_columns[idx] = item
                    # Adds the custom column where I can generate info
                    if item == 'Measurement':
                        chosen_columns['Measurement'] = 'Measurement'
                        chosen_columns['Measurement Unit'] = 'Measurement Unit'
                    elif item not in all_columns.values():
                        chosen_columns[item] = item

        chosen_columns_keys = list(chosen_columns.keys())

        # Loading some data if these columns exist
        if 'Space' in chosen_columns_keys:
            spaces_vertices = self.spaces(output="vertices")
            spaces_check = True if self.get_all_spaces() is not None else False

        if 'Page Label' or 'Page Number' or 'Space' in chosen_columns_keys:
            markup_index = self.get_markups_index()

        if 'Page Label' in chosen_columns_keys:
            page_label_index = self.get_page_labels()

        data = {'markups': []}

        # Pull the data out
        for markup in self.get_markups_list():
            # Fresh row
            row_dict = {}
            for column in chosen_columns_keys:
                # Too much confusion if no subject
                if markup[column] is not None or column in custom_columns and markup['/Subj']:
                    if column == '/OC':
                        row_dict[chosen_columns['/OC']] \
                            = markup['/OC'].Name[1:-1]
                    elif column == '/IT':
                        row_dict[chosen_columns[column]] = markup[column]
                    # Subject is needed to filter down results
                    elif column == 'Page Number':
                        row_dict[chosen_columns[column]] \
                            = markup_index[markup.NM] + 1
                    elif column == 'Page Label':
                        if markup_index[markup.NM] is not None:
                            row_dict['Page Label'] \
                                = page_label_index[markup_index[markup.NM]]
                    elif column in first_slice:
                        row_dict[chosen_columns[column]] = markup[column][1:]
                    elif column in no_mod:
                        row_dict[chosen_columns[column]] = markup[column]
                    elif column == '/DepthUnit':
                        row_dict[chosen_columns[column]] = markup[column][0]
                    elif column == '/Contents':
                        row_dict[chosen_columns[column]] \
                            = content_hex_convert(markup[column])
                    elif column == '/AP':
                        row_dict[chosen_columns[column]] = markup[column].N
                    elif column in pdf_dates:
                        row_dict[chosen_columns[column]] = date_string(markup[column])
                    elif column == '/MeasurementTypes':
                        row_dict[chosen_columns[column]] \
                            = measurement_types[markup[column]]
                    # Handles imperial only for now
                    elif column == 'Measurement':
                        measurements = measurement_col(markup)
                        row_dict['Measurement'] = measurements[0]
                        row_dict['Measurement Unit'] = measurements[1]
                    elif column in color_columns:
                        row_dict[chosen_columns[column]] = color_to_num(markup[column])
                    elif column == "Measurement Unit":
                        pass
                    elif column == "Space":
                        row_dict['Space'] = markup_space(markup, spaces_check, markup_index[markup.NM], spaces_vertices)
                    elif column in parenthesis_drop:
                        row_dict[chosen_columns[column]] = markup[column][1:-1]
                    elif markup[column] is not None:
                        row_dict[chosen_columns[column]] = markup[column]
                    else:
                        pass
                else:
                    pass
            data['markups'].append(row_dict)
        return data
