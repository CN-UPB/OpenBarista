import sys

relation = sys.argv[1]
port = sys.argv[2]
iface = sys.argv[3]
ip = sys.argv[4]
external = sys.argv[5]
file_path = sys.argv[6]

if external == "true":
    netmask = "255.255.0.0"
else:
    netmask = "255.255.255.0"

text = "# relation = " + relation + "\n"\
    + "# port = " + port + "\n"\
    + "auto " + iface + "\n"\
    + "iface " + iface + " inet static\n"\
    + "\taddress " + ip + "\n"\
    + "\tnetmask " + netmask + "\n\n"

# Read in the file
filedata = None
with open(file_path, 'r') as file :
    filedata = file.read()

if external == "true":
    # put the new interface at the end of the file
	filedata += text
else:
    # put the new interface directly before the external edges
    to_replace = "# EXTERNAL EDGES"
    replace_by = text + "# EXTERNAL EDGES"
    filedata = filedata.replace(to_replace, replace_by)

# Write the file out again
with open(file_path, 'w') as file:
    file.write(filedata)


