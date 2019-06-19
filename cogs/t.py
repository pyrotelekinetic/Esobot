import os
import json
import string

from unidecode import unidecode

os.system("python3 -m pip install unidecode --user")
with open("config/messages.json") as f:
    jj = json.load(f)
    nn = ["".join([x for x in unidecode(m.strip().casefold()) if x in string.ascii_letters]) for m in jj]
with open("config/messages.json", "w") as f:
    json.dump(nn, f)
