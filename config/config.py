# Import(s)
from util.dict_obj import DictObj
import json

# Export configs
arguments = DictObj(json.load(open("./config/arguments.json")))
config = DictObj(json.load(open("./config/config.json")))
