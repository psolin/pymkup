from datetime import datetime
from fractions import Fraction
from time import mktime, strptime
from matplotlib.colors import to_hex
import matplotlib.patches as patches
from column_data import lf_columns
import pdfreader.types as t


def tuple_float(point_list):
    poly_points_int = []
    for point in point_list:
        poly_points_int.append((float(point[0]), float(point[1])))
    return poly_points_int


# /Contents conversion into something more meaningful
def content_hex_convert(content):
    if content is None:
        return None

    if type(content) == t.native.String:
        content = content.decode("ISO-8859-1")

    if "FEFF" in str(content):
        content = bytes.fromhex(content[4:])
        content = str(content, 'ASCII')
        content = content.splitlines()[1]
        content = content.replace('\x00', '')

    return content


def feet_inches_convert(text):
    feet, sep, inches = text.rpartition("\'")
    if sep != "\'":
        return ''
    inches = inches
    feet = float(feet)
    inches = inches.replace("-", "")
    inches = inches.replace('"', '')
    if ' ' in inches:
        inches_whole, inches_fract = inches.split(' ')
        a = Fraction(inches_fract)
        inches = (float(a) + float(inches_whole)) / 12
    elif inches == 0:
        a = Fraction(str(inches))
        inches = float(a) / 12
    elif '/' in inches:
        a = Fraction(str(inches))
        inches = float(a) / 12
    else:
        inches = float(inches) / 12
    return feet + inches


def measurement_col(markup):
    measurements = []
    if "sf" in str(content_hex_convert(markup['Contents'])):
        sf_measure = content_hex_convert(
            markup['Contents']).split(' ')
        measurements.append([float(sf_measure[0]), sf_measure[1]])
    elif markup['IT'] == "PolygonCount":
        measurements.append([1, "Count"])
    elif markup['IT'] in lf_columns:
        measurements.append([
            feet_inches_convert(content_hex_convert(
                markup['Contents'])),
            'ft\' in\"'])
    elif markup['IT'] == 'PolygonRadius':
        r_measure = content_hex_convert(markup['Contents'])
        measurements.append([
            feet_inches_convert(r_measure),
            'ft\' in\"'])
    elif markup['IT'] == 'PolygonVolume':
        sf_measure = content_hex_convert(
            markup['Contents']).split(" ", 1)
        measurements.append([float(sf_measure[0]), sf_measure[1]])
    elif markup['IT'] == 'PolyLineAngle':
        measurements.append([
            content_hex_convert(markup['Contents']),
            '°'])
    elif markup.Subtype == 'PolyLine':
        '''
        markup_rect = [*zip(list(markup.Vertices)[::2],
                            list(markup.Vertices)[1::2])]
        markup_rect = tuple_float(markup_rect)
        line = LineString(markup_rect)
        '''
        measurements = [[0, 'length']]
    else:
        pass
    return measurements[0]


def markup_space(markup, space_check, page_index, spaces_vertices):
    if markup.get('Vertices', None) is not None and space_check is True:
        markup_spaces = []
        # Convert markup.Rect to something more usable
        markup_rect = [*zip(list(markup.Vertices)[::2],
                            list(markup.Vertices)[1::2])]
        markup_rect = tuple_float(markup_rect)

        for space_vert in spaces_vertices[page_index]:
            for key, value in space_vert.items():
                poly_points = list(tuple(sub) for sub in list(value))
                poly_points = tuple_float(poly_points)
                space_polygon = patches.Polygon(poly_points)
                point_check = 0
                for point in markup_rect:
                    if space_polygon.contains_point(point) is True:
                        point_check += 1
                if float(point_check)/float(len(poly_points)) > 0.5:
                    markup_spaces.append(key)
        return markup_spaces
    else:
        return []


def date_string(markup):
    datestring = markup[2:-7]
    ts = strptime(datestring, "%Y%m%d%H%M%S")
    dt = datetime.fromtimestamp(mktime(ts))
    return dt


def color_to_num(color_string):
    for i in range(0, len(color_string)):
        color_string[i] = int(color_string[i])
    return to_hex(tuple(color_string))
