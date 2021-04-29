from pymkup import pymkup

#basic test to see if returned someone correct
def test_spaces():
	x = pymkup("/markup-deep-spaces.pdf")
	spaces = x.spaces()
	assert 'spaces' in spaces

#basic test to see if returned someone correct
def test_markup():
	x = pymkup("/markup-deep-spaces.pdf")
	markup = x.markups()
	assert 'markups' in markup