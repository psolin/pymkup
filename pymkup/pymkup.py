from os.path import dirname, realpath
from pdfreader import PDFDocument
from column_data import *
from data_conversion import *


class Pymkup:
    def __init__(self, file):
        try:
            self.file = file
            self.inpfn = dirname(realpath(__file__)) + self.file
            self.fd = open(self.inpfn, "rb")
            self.template_pdf = PDFDocument(self.fd)
            # Checking if the PDF was authored by BB
            "Bluebeam" in self.template_pdf.metadata['Creator']

            self.all_pages = [p for p in self.template_pdf.pages()]
            self.spaces_path = {}
        except Exception:
            print(self.inpfn, "doesnt exist.")

    # Extract the page labels into a dictionary
    # This is broken for some files because of the hierarchy.
    def get_page_labels(self):
        page_label_dict = {}
        # This will work if there are any page labels
        if self.template_pdf.root.PageLabels is not None:
            page_num_list = self.template_pdf.root.PageLabels.Nums
            for idx, page in enumerate(page_num_list[1::2]):
                if page.P is not None:
                    page_label_dict[idx] = page.P.decode("utf-8")
                else:
                    page_label_dict[idx] = "Page " + str(idx + 1)
        else:
            for idx, page in enumerate(self.all_pages):
                page_label_dict[idx] = "Page " + str(idx + 1)
        return page_label_dict

    # Extracting the entire markups list
    def get_markups_list(self):
        markups_list = []
        for idx, page in enumerate(self.all_pages):
            if page.Annots is not None:
                for annotation in page.Annots:
                    markups_list.append(annotation)
        return markups_list

    # Indexing the markups to their respective pages by UUID
    def get_markups_index(self):
        markups_index = {}
        for idx, page in enumerate(self.all_pages):
            if len(page.Annots) > 0:
                for num, annotation in enumerate(page.Annots):
                    markups_index[annotation.NM] = idx
        return markups_index

    def get_columns(self):

        # Taking the current column list across pages in the file and putting
        # it into in a dictionary
        column_list = []
        column_dict = {}
        for page in self.all_pages:
            if len(page.Annots[0]) > 0:
                for column in page.Annots[0]:
                    column_list.append(column)

        # Remove dupes
        [i for n, i in enumerate(column_list) if i not in column_list[:n]]

        # Create dictionary with original name and corrected names
        for column in column_list:
            column_dict[column] = column_data[column]

        return column_dict

    def get_all_spaces(self):
        space_list = []
        space_dict = {}
        for idx, page in enumerate(self.all_pages):
            if page.BSISpaces is not None:
                for space in page.BSISpaces:
                    space_list.append(space)
            space_dict[idx] = space_list
            space_list = []
        return space_dict

    def spacesdict(self, spaces, key, prevparent):
        for item in spaces:
            self.spaces_path[key].append({item.Title.decode("utf-8"): item.Path})
            prevparent[item.Title.decode("utf-8")] = {}
            if item.Kids is not None:
                prevparent[item.Title.decode("utf-8")] \
                    = self.spacesdict(item.Kids, key, {})

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
            space_check = any(self.get_all_spaces().values())

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
                if markup.get(column, None) is not None or column in custom_columns and markup['Subj']:
                    if column == 'OC':
                        row_dict[chosen_columns['OC']] \
                            = markup['OC'].Name.decode("utf-8")
                    elif column == 'IT':
                        row_dict[chosen_columns[column]] = markup[column]
                    # Subject is needed to filter down results
                    elif column == 'Page Number':
                        row_dict[chosen_columns[column]] \
                            = markup_index[markup.NM] + 1
                    elif column == 'Page Label':
                        if markup_index[markup.NM] is not None:
                            row_dict['Page Label'] \
                                = page_label_index.get(markup_index[markup.NM], None)
                    elif column in no_mod:
                        row_dict[chosen_columns[column]] = markup[column]
                    elif column == 'DepthUnit':
                        row_dict[chosen_columns[column]] = markup[column][0]
                    elif column == 'Contents':
                        row_dict[chosen_columns[column]] \
                            = content_hex_convert(markup[column])
                    elif column == 'AP':
                        row_dict[chosen_columns[column]] = markup[column].N
                    elif column in pdf_dates:
                        row_dict[chosen_columns[column]] = date_string(markup[column].decode("utf-8"))
                    elif column == 'MeasurementTypes':
                        row_dict[chosen_columns[column]] \
                            = measurement_types[markup[column]]
                    # Handles imperial only for now
                    elif column == 'Measurement':
                        if markup.get('Contents', None) is not None:
                            measurements = measurement_col(markup)
                            row_dict['Measurement'] = measurements[0]
                            row_dict['Measurement Unit'] = measurements[1]
                    elif column in color_columns:
                        if len(markup[column]) == 3:
                            row_dict[chosen_columns[column]] = color_to_num(markup[column])
                        else:
                            row_dict[chosen_columns[column]] = markup[column]
                    elif column == "Measurement Unit":
                        pass
                    elif column == "Space":
                        row_dict['Space'] = markup_space(markup, space_check, markup_index[markup.NM], spaces_vertices)
                    elif column in decode_col:
                        row_dict[chosen_columns[column]] = markup[column].decode("ISO-8859-1")
                    elif markup[column] is not None:
                        row_dict[chosen_columns[column]] = markup[column]
                    else:
                        pass
                else:
                    pass
            data['markups'].append(row_dict)
            print(row_dict)
        return data
