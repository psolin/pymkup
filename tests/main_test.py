from pymkup import pymkup

def spaces_returned_dict():
	x = pymkup("\\tests\\markup-deep-spaces.pdf")
	spaces = x.spaces()
	assert 'spaces' in spaces

def markup_returned_dict():
	x = pymkup("\\tests\\markup-deep-spaces.pdf")
	markup = x.markups()
	assert 'markups' in markup