# Import(s)
from util.dict_obj import DictObj
import json

# Export configs
config = DictObj(json.load(open("./config/config.json")))
