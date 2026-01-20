'''
Removes the 'active_missions_v2.json' file from a .compcon backup.
Takes two in-line arguments:

in_file (str): Filename for the original .compcon backup to read.
out_file (str): Filename for the modified .compcon backup being written.
'''

import json
import sys

in_file = sys.argv[1]
out_file = sys.argv[2]

with open(in_file, "r+", encoding="utf8") as f:
    compcon_data = json.load(f)

for i, file_dict in enumerate(compcon_data):
    if file_dict.get("filename") == "active_missions_v2.json":
        compcon_data.pop(i)
        break

with open(out_file, "w+", encoding="utf8") as f:
    json.dump(compcon_data, f)