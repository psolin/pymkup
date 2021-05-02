from fractions import Fraction
from column_data import lf_columns
from shapely.geometry import LineString
from shapely.geometry import Point, Polygon
from datetime import datetime
from time import mktime
from time import strptime
from colormap import Color

def tuple_float(point_list):
    poly_points_int = []
    for point in point_list:
        poly_points_int.append((float(point[0]), float(point[1])))
    return poly_points_int


# /Contents conversion into something more meaningful
def content_hex_convert(content):
    if content is None:
        return None

    try:
        if "feff" in content:
            content = content.decode_hex()
            content = content.decode('utf-16')
            content = content.splitlines()[1]
    except Exception:
        pass

    # Remove the parenthesis
    if content[0] == "(":
        content = content[1:-1]

    return content


def feet_inches_convert(text):
    feet, sep, inches = text.rpartition("\'")
    if sep != "\'":
        return ''
    inches = (inches[1:-1])
    feet = float(feet)
    if ' ' in inches:
        inches_whole, inches_fract = inches.split(' ')
        a = Fraction(inches_fract)
        inches = (float(a) + float(inches_whole)) / 12
    elif inches == 0:
        pass
    elif '/' in inches:
        a = Fraction(str(inches))
        inches = float(a) / 12
    else:
        inches = float(inches) / 12
    return feet + inches


def measurement_col(markup):
    measurements = []
    if "sf" in str(content_hex_convert(markup['/Contents'])):
        sf_measure = content_hex_convert(
            markup['/Contents']).split(' ')
        measurements.append([sf_measure[0], sf_measure[1]])
    elif markup['/IT'] == "/PolygonCount":
        measurements.append([1, "ct"])
    elif markup['/IT'] in lf_columns:
        measurements.append([
            feet_inches_convert(content_hex_convert(
                markup['/Contents'])),
            'lf'])
    elif markup['/IT'] == '/PolygonRadius':
        r_measure = content_hex_convert(markup['/Contents'])
        measurements.append([
            feet_inches_convert(r_measure),
            'r ft'])
    elif markup['/IT'] == '/PolygonVolume':
        sf_measure = content_hex_convert(
            markup['/Contents']).split(" ", 1)
        measurements.append([sf_measure[0], sf_measure[1]])
    elif markup['/IT'] == '/PolyLineAngle':
        measurements.append([
            content_hex_convert(markup['/Contents']),
            'angle'])
    elif markup.Subtype == '/PolyLine':
        markup_rect = [*zip(list(markup.Vertices)[::2],
                            list(markup.Vertices)[1::2])]
        markup_rect = tuple_float(markup_rect)
        line = LineString(markup_rect)
        measurements = [[line.length, 'length']]
    else:
        pass
    return measurements[0]


def markup_space(markup, page_index, spaces_vertices):
    if markup['/Vertices']:
        markup_spaces = []
        # Convert markup.Rect to something more usable
        markup_rect = [*zip(list(markup.Vertices)[::2],
                            list(markup.Vertices)[1::2])]
        markup_rect = tuple_float(markup_rect)

        for space_vert in spaces_vertices[page_index]:
            for key, value in space_vert.items():
                poly_points = list(tuple(sub) for sub in list(value))
                poly_points = tuple_float(poly_points)
                space_polygon = Polygon(poly_points)
                true_check = 0
                for point in markup_rect:
                    if space_polygon.contains(Point(point)) is True:
                        true_check += 1
                    if true_check == len(poly_points):
                        markup_spaces.append(key)
        return markup_spaces
    else:
        return


def date_string(markup):
    datestring = markup[3:-8]
    ts = strptime(datestring, "%Y%m%d%H%M%S")
    dt = datetime.fromtimestamp(mktime(ts))
    return dt


def color_to_num(color_string):
    for i in range(0, len(color_string)):
        color_string[i] = int(color_string[i])
    tuple(color_string)
    return Color(rgb=color_string).hex
