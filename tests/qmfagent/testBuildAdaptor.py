# Copyright (C) 2010 Red Hat, Inc.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.


import unittest
from builders import *
from qmfagent.BuildAdaptor import BuildAdaptor

class TestBuildAdaptor(unittest.TestCase):
    def setUp(self):
        self.schema = BuildAdaptor.qmf_schema
        self.tdl_string = """\
        <template>
          <name>f14jeos</name>
          <os>
            <name>Fedora</name>
            <version>14</version>
            <arch>x86_64</arch>
            <install type='url'>
              <url>http://download.fedoraproject.org/pub/fedora/linux/releases/14/Fedora/x86_64/os/</url>
            </install>
          </os>
          <description>Fedora 14</description>
        </template>
		"""
	
    def tearDown(self):
        self.schema = None
        self.tdl_string = None
    
    def testQMFSchemaDefinition(self):
        expected_schema_properties = ("descriptor", "target", "status", "percent_complete", "finished_image")
        for schema_property in self.schema.getProperties():
            self.assert_(schema_property.getName() in expected_schema_properties)
	
    def testInstantiateMockBuilder(self):
        build_adaptor = BuildAdaptor(self.tdl_string, "mock", "foo", "bar")
        self.assertIsInstance(build_adaptor.builder, MockBuilder.MockBuilder)
        self.assert_(build_adaptor.descriptor == self.tdl_string)
        self.assert_(build_adaptor.target == "mock")
    
    # def testInstantiateFedoraBuilder(self):
    #     build_adaptor = BuildAdaptor(self.tdl_string, "foo", "bar", "baz")
    #     self.assertIsInstance(build_adaptor.builder, FedoraBuilder.FedoraBuilder)
    

if __name__ == '__main__':
	unittest.main()