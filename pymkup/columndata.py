column_data = {
        # Thanks to terminalworks.com, 
        # PDF-Class-raku for some definititions.


        # Default Columns
        
        # Text representing a short description of 
        # the subject being addressed by the annotation.
        '/Subj' : 'Subject',
        '/CreationDate' : 'Creation Date',
        '/Label' : 'Label',
        # By convention, this entry identifies the 
        # user who added the annotation.
        '/T' : 'Author',
        # Optional Content Group as 'Name' key
        '/OC' : 'Layer',
        # The date and time when the annotation 
        # was most recently modified.
        '/M' : 'Date',
        # Text to be displayed for the annotation or, if this type 
        # of annotation does not display text, an alternate description 
        # of the annotation’s contents in human-readable form.
        # Hex text "Comment" column.
        '/Contents' : 'Comments',  


        # Known Properties
        
        # Scale where the markup falls and the multiplier
        '/BBMeasure' : 'BBMeasure',
        # Describes the appearance of XObjects
        '/AP' : 'AP',
        # Measurement Properties
        '/MeasurementTypes' : 'Measurement Types',
        '/Measure' : 'Measure',  # Measurement Properties
        '/RC' : 'Rich Text',  # Segment Rich Text Appearance
        # The constant opacity value to be used 
        # in painting the annotation.
        # Opacity Property
        '/CA' : 'Opacity',  
        '/CountScale' : 'Scale',  # Scale Property
        # Custom columns options and selections
        '/BSIColumnData' : 'BSIColumnData',
        '/DS' : 'DS',  # Caption font and style
        # Area Mesurement/Length Measurement
        '/SlopeType' : 'Slope Type',
        # Related to pitch and run, slope properties
        '/PitchRun' : 'Pitch/Run',
        '/DepthUnit' : 'Depth Unit',
        '/Depth' : 'Depth',
        # Start/End Line Cap in Length Measurement
        '/LE' : 'Length Caps',
        # Line Width in Length Measurement
        '/LLE' : 'Length Line Width',
        # The box where the entire line/lead is located
        '/L' : 'Length Box',


        # Hidden Properties
        
        # Primary key for markup aka "annotation name"
        '/NM' : 'UUID', 
        # Groupings by UUID and subject (>1)
        '/GroupNesting' : 'Group Nesting',
        # The type of PDF object that this dictionary describes
        '/Type' : 'Type', 
        # The type of annotation that this dictionary describes.
        #Shape parent catagory
        '/Subtype' : 'Subtype',  
        '/CountStyle' : 'Count Style',  # Count tool shape style
        #Exact layout of the markup in x,y coordinates
        '/Vertices' : 'Vertices',
        #Border Style
        '/BS' : 'BS', 
        # The annotation rectangle, defining the location of 
        # the annotation on the page in default user space units.
        '/Rect' : 'Rectangle',
        # The count of the larger group where the markup is nested
        '/NumCounts' : 'NumCounts',
        #"Intent", type of counting (measurement)
        '/IT' : 'Intent',
        #Polylength tool Rise/Drop value
        '/RiseDrop' : 'Rise/Drop',
        # An action to be performed when the annotation is activated.
        '/A' : 'A', 
        # Color
        '/C' : 'Color',
        # Interior Color
        '/IC' : 'Interior Color',
        # A set of flags specifying various characteristics 
        # of the annotation. Default value: 0.
        '/F' : 'Flags',


        # Unknown Properties
        
        '/P' : 'P',  # All of the data combined
        '/Version' : 'Version',  # Versioning, not sure how
        '/LL' : 'LL',  # Another Length Property
        # T/F - may be related to measurement or not
        '/Cap' : 'Cap',
        '/AlignOnSegment' : 'Align On Segment',
        '/Border' : 'Border',
        '/BSIBatchQuery' : 'BSIBatchQuery',
        # Possibly a link property
        '/QuadPoints' : 'QuadPoints',
        '/Dest' : 'Dest',
        # Rectangle differences
        '/RD' : 'RD'
}


# Group by data output formatting

#markup[column][1:]
first_slice = ['/Type', '/CountStyle', '/Subtype']

#markup[column]
no_mod = [
'/NumCounts', 
'/Version', 
'/GroupNesting', 
'/Version', 
'/F', 
'/BS', 
'/IC',
'/DS',
'/BSIColumnData',
'/Vertices',
'/Rect',
'/Version',
'/BBMeasure',
'/CA'
]

#PDF Dates
pdf_dates = ['/CreationDate', '/M']

#lf column values
lf_columns = [
'/PolyLineDimension', 
'/LineDimension', 
'/CircleDimension']


# Other column data

custom_columns = [
'Measurement', 
'Type', 
'Page Label', 
'Page Number', 
'Space']

default_columns = {
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
            '/OC': 'Layer',
            'Space': 'Space'}

measurement_types = {
        '128': "Count",
        '129': "Shape",
        '130': "Length",
        '132': "Volume",
        '384': "Diameter",
        '1152': "Angle"}