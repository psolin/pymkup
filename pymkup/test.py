from pymkup import pymkup
import json

x = pymkup("/tests/markup-deep-spaces.pdf")
y = x.spaces()
print(json.dumps(y, indent=4, default=str))