##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import sys

interface_instance_id = sys.argv[1]
type = sys.argv[2]
internal = sys.argv[3]
external = sys.argv[4]
iface = sys.argv[5]
internal_or_public = sys.argv[6]
file_path = sys.argv[7]

text = "# interface_instance_id = " + interface_instance_id + "\n"\
    + "# type = " + type + "\n"\
    + "# internal = " + internal + "\n"\
    + "# external = " + external + "\n"\
    + "auto " + iface + "\n"\
    + "iface " + iface + " inet dhcp\n\n"

# Read in the file
filedata = None
with open(file_path, 'r') as file :
    filedata = file.read()

if internal_or_public == "public":
    # put the new interface at the end of the file
	filedata += text
else:
    # put the new interface directly before the external edges
    to_replace = "# PUBLIC PORTS"
    replace_by = text + "# PUBLIC PORTS"
    filedata = filedata.replace(to_replace, replace_by)

# Write the file out again
with open(file_path, 'w') as file:
    file.write(filedata)


