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
import re

interface_instance_id = sys.argv[1]
file_path = sys.argv[2]

# Read in the file
filedata = None
with open(file_path, 'r') as file :
    filedata = file.read()

reg_expression = r"# interface_instance_id = " + re.escape(interface_instance_id) + r"\n"\
    + r"# type = [\w,\.,\-]+?\n"\
    + r"# internal = [\w,\.,\-]+?\n"\
    + r"# external = [\w,\.,\-]+?\n"\
    + r"auto [\w,\.,\-]+?\n"\
    + r"iface [\w,\.,\-]+? inet dhcp\n\n"

m = re.search(reg_expression, filedata)

if m is not None:
    text_to_delete = m.group(0)
    filedata = filedata.replace(text_to_delete, "")

    # Write the file out again
    with open(file_path, 'w') as file:
        file.write(filedata)

else:
    print("Interface not found.")