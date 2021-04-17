column_data = {
        # These are the default columns
        '/Subj' : 'Subject',
        '/CreationDate' : 'Creation Date',
        '/Label' : 'Label',
        '/T' : 'Author',
        # Optional Content Group as 'Name' key
        '/OC' : 'Layer',
        '/M' : 'Date',  # Technically 'modified' date
        '/Contents' : 'Comments',  # Hex text comment

        # These are hidden properties
        '/NM' : 'PK',  # Primary Key for Markup
        # Groupings by primary key and subject (>1)
        '/GroupNesting' : 'Group Nesting',
        '/Type' : 'Type',  # Annotation (markup) or otherwise
        '/Subtype' : 'Subtype',  # Shape parent catagory
        '/CountStyle' : 'Count Style',  # Count tool shape style
        # Exact layout of the markup in x,y coordinates
        '/Vertices' : 'Vertices',
        '/BS' : 'BS',  # Markup style
        '/Rect' : 'Rectangle',  # Rectanular Coordinates
        # The count of the larger group where the markup is nested
        '/NumCounts' : 'NumCounts',
        '/IT' : 'IT',  # Type of counting (measurement)

        # Properties
        # Scale where the markup falls and the multiplier
        '/BBMeasure' : 'BBMeasure',
        # Describes the XObjects
        '/AP' : 'AP',
        # Measurement Properties
        '/MeasurementTypes' : 'Measurement Types',
        '/Measure' : 'Measure',  # Measurement Properties
        '/RC' : 'Rich Text',  # Segment Rich Text Appearance
        '/CA' : 'Opacity',  # Opacity Property
        '/CountScale' : 'Scale',  # Scale Property
        # Custom columns options and selections
        '/BSIColumnData' : 'BSIColumnData',
        '/DS' : 'DS',  # Caption font and style
        # Area Mesurement/Length Measurement
        '/SlopeType' : 'Slope Type',
        # Related to pitch and run, slope properties
        '/PitchRun' : 'PitchRun',
        '/DepthUnit' : 'Depth Unit',
        '/Depth' : 'Depth',
        # Start/End Line Cap in Length Measurement
        '/LE' : 'Length Caps',
        # Line Width in Length Measurement
        '/LLE' : 'Length Line Width',
        # The box where the entire line/lead is located
        '/L' : 'Length Box',

        # These are hidden/unknown columns to me
        '/P' : 'P',  # All of the data combined
        # This may be if something is checked or not
        '/F' : 'F',
        # Unknown three option list, possibly status
        '/C' : 'C',
        # Mirrors C but returns empty list instead of blank with text
        '/IC' : 'IC',
        '/Version' : 'Version',  # Versioning, not sure how
        '/LL' : 'LL',  # Another Length Property
        # T/F - may be related to measurement or not
        '/Cap' : 'Cap',
        '/RiseDrop' : 'Rise Drop',
        '/AlignOnSegment' : 'Align On Segment',
        '/A' : 'A',
        '/Border' : 'Border',
        '/BSIBatchQuery' : 'BSIBatchQuery',
        '/QuadPoints' : 'QuadPoints',
        '/Dest' : 'Dest',
        '/RD' : 'RD'
}