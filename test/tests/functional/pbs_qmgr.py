# coding: utf-8

# Copyright (C) 1994-2017 Altair Engineering, Inc.
# For more information, contact Altair at www.altair.com.
#
# This file is part of the PBS Professional ("PBS Pro") software.
#
# Open Source License Information:
#
# PBS Pro is free software. You can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# PBS Pro is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Commercial License Information:
#
# The PBS Pro software is licensed under the terms of the GNU Affero General
# Public License agreement ("AGPL"), except where a separate commercial license
# agreement for PBS Pro version 14 or later has been executed in writing with
# Altair.
#
# Altair’s dual-license business model allows companies, individuals, and
# organizations to create proprietary derivative works of PBS Pro and
# distribute them - whether embedded or bundled with other software - under
# a commercial license agreement.
#
# Use of Altair’s trademarks, including but not limited to "PBS™",
# "PBS Professional®", and "PBS Pro™" and Altair’s logos is subject to Altair's
# trademark licensing policies.

import os

from tests.functional import *
from ptl.lib.pbs_ifl_mock import *


class TestQmgr(TestFunctional):
    """
    Test suite for PBSPro's qmgr command
    """

    def __check_whitespace_prefix(self, line):
        """
        Check whether the whitespace prefix for the line specified is correct

        :param line: the line to check
        :type line: String
        """
        if line is None:
            return

        if line[0] == " ":
            # Spaces are the prefix for new attribute lines
            # Make sure that this is a new attribute line
            self.assertTrue("=" in line)
        elif line[0] == "\t":
            # Tabs are prefix for line extensions
            # Make sure that this is a line extension
            self.assertTrue("=" not in line)

    def test_listcmd_whitespaces(self):
        """
        Check that the prefix for new attributes listed out by qmgr list
        are spaces and that for line extensions is a tab
        """
        fn = self.du.create_temp_file()
        node_prefix = "vn"
        nodename = node_prefix + "[0]"
        vndef_file = None
        try:
            # Check 1: New attributes are prefixed with spaces and not tabs
            # Execute qmgr -c 'list sched' and store output in a temp file
            if self.du.is_localhost(self.server.hostname) is True:
                qmgr_cmd = ["qmgr", "-c", "list sched"]
            else:
                qmgr_cmd = ["qmgr", "-c", "\'list sched\'"]
            with open(fn, "w+") as tempfd:
                ret = self.du.run_cmd(self.server.hostname, qmgr_cmd,
                                      stdout=tempfd)

                self.assertTrue(ret['rc'] == 0)
                for line in tempfd:
                    self.__check_whitespace_prefix(line)

            # Check 2: line extensions are prefixed with tabs and not spaces
            # Create a random long, comma separated string
            blah = "blah"
            long_string = ""
            for i in range(49):
                long_string += blah + ","
            long_string += blah
            # Create a new vnode
            attrs = {ATTR_rescavail + ".ncpus": 2}
            self.server.create_vnodes(node_prefix, attrs, 1, self.mom)
            # Set 'comment' attribute to the long string we created above
            attrs = {ATTR_comment: long_string}
            self.server.manager(MGR_CMD_SET, VNODE, attrs, nodename)
            # Execute "qmgr 'list node vn[0]'"
            # The comment attribute should generate a line extension
            if self.du.is_localhost(self.server.hostname) is True:
                qmgr_cmd = ["qmgr", "-c", "list node " + nodename]
            else:
                qmgr_cmd = ["qmgr", "-c", "\'list node " + nodename + "\'"]
            with open(fn, "w+") as tempfd:
                ret = self.du.run_cmd(self.server.hostname, qmgr_cmd,
                                      stdout=tempfd)
                self.assertTrue(ret['rc'] == 0)
                for line in tempfd:
                    self.__check_whitespace_prefix(line)

        finally:
            # Cleanup
            # Remove the temporary file
            os.remove(fn)
            # Delete the vnode created
            if vndef_file is not None:
                self.mom.delete_vnodes()
                self.server.manager(MGR_CMD_DELETE, VNODE, id=nodename)
