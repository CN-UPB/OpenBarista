import sys
import re

iface = sys.argv[1]
file_path = sys.argv[2]

# Read in the file
filedata = None
with open(file_path, 'r') as file :
    filedata = file.read()

reg_expression = r"# relation = [\w,\.,\-]+?\n"\
    + r"# port = [\w,\.,\-]+?\n"\
    + r"auto " + re.escape(iface) + r"\n"\
    + r"iface " + re.escape(iface) + r" inet static\n"\
    + r"\taddress [\w,\.,\-]+?\n"\
    + r"\tnetmask [\w,\.,\-]+?\n\n"

m = re.search(reg_expression, filedata)

if m is not None:
    text_to_delete = m.group(0)
    filedata = filedata.replace(text_to_delete, "")

    # Write the file out again
    with open(file_path, 'w') as file:
        file.write(filedata)

else:
    print("Edge not found.")