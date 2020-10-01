# Unit testing for the hcds_responder_base.BaseResponder class.
#
# Copyright 2020 Alexandre Emsenhuber
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import urllib.parse

import hcds_responder_base

class BaseResponderTestCase( unittest.TestCase ):
	def make_obj( self, config = {}, url = None, sub = None, query = None ):
		resp = hcds_responder_base.BaseResponder( config )

		resp.set_request( {}, None )

		if not url is None:
			resp.set_url( url, sub )

		if not query is None:
			resp.set_query( query )

		return resp

	def test_get_config_none( self ):
		resp = self.make_obj( {} )

		self.assertEqual( resp.get_config( "none" ), None )
		self.assertEqual( resp.get_config( "none", 123. ), 123. )

	def test_get_config_one( self ):
		resp = self.make_obj( { "key": "value" } )

		self.assertEqual( resp.get_config( "key" ), "value" )
		self.assertEqual( resp.get_config( "key", 123. ), "value" )

		self.assertEqual( resp.get_config( "none" ), None )
		self.assertEqual( resp.get_config( "none", 123. ), 123. )

	def test_url_none( self ):
		resp = self.make_obj()

		with self.assertRaises( Exception ):
			resp.get_param( "none" )

	def test_url( self ):
		resp = self.make_obj( url = urllib.parse.urlparse( "http://ihave/no/idea?what=to#write" ), sub = "ideal" )

		self.assertEqual( resp.get_sub(), "ideal" )

		self.assertEqual( resp.get_param( "what" ), "to" )

		self.assertEqual( resp.get_config( "none" ), None )
		self.assertEqual( resp.get_config( "none", 123. ), 123. )

	def test_output_none( self ):
		resp = self.make_obj()

		self.assertEqual( resp.get_output(), [] )

	def test_output_one( self ):
		resp = self.make_obj()

		resp.add_output( "Plain text" )

		self.assertEqual( resp.get_output(), [ "Plain text" ] )

	def test_parse_float_query( self ):
		resp = self.make_obj( query = "empty=&text=invalid&number=12.34&two=1.23&two=2.34&nan=nan&inf=inf" )

		self.assertEqual( resp.parse_float_query( "empty" ), None )
		self.assertEqual( resp.parse_float_query( "text" ), None )
		self.assertEqual( resp.parse_float_query( "number" ), 12.34 )
		self.assertEqual( resp.parse_float_query( "two" ), 1.23 )
		self.assertEqual( resp.parse_float_query( "nan" ), None )
		self.assertEqual( resp.parse_float_query( "inf" ), None )

	def test_parse_list_query( self ):
		resp = self.make_obj( query = "good=one&bad=invalid" )
		allowed = [ "one", "two" ]

		self.assertEqual( resp.parse_list_query( "good", allowed ), "one" )
		self.assertEqual( resp.parse_list_query( "bad", allowed ), None )

if __name__ == '__main__':
	unittest.main()
