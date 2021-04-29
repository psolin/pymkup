from pymkup import pymkup
import json

x = pymkup("/tests/measure.pdf")
y = x.markups()
print(json.dumps(y, indent=4, default=str))