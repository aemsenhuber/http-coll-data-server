# Unit testing for the hcds_responder_coll.CollResponder class.
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
import hcds_responder_coll

class CollResponderTestCase( unittest.TestCase ):
	def make_obj( self, query ):
		resp = hcds_responder_coll.CollResponder( {} )
		resp.set_request( {}, None )
		resp.set_query( query )
		return resp

	def test_retrieve_body_mass_neg( self ):
		resp = self.make_obj( "mtar_value=-1&mtar_unit=kg" )

		mass, retp = resp.retrieve_body_mass( "tar" )

		self.assertEqual( mass, None )
		self.assertEqual( retp[ "mtar_value" ], None )
		self.assertEqual( retp[ "mtar_unit" ], "kg" )

	def test_retrieve_body_mass_zero( self ):
		resp = self.make_obj( "mtar_value=0&mtar_unit=kg" )

		mass, retp = resp.retrieve_body_mass( "tar" )

		self.assertEqual( mass, None )
		self.assertEqual( retp[ "mtar_value" ], None )
		self.assertEqual( retp[ "mtar_unit" ], "kg" )

	def test_retrieve_body_mass_invalidunit( self ):
		resp = self.make_obj( "mtar_value=1&mtar_unit=pound" )

		mass, retp = resp.retrieve_body_mass( "tar" )

		self.assertEqual( mass, None )
		self.assertEqual( retp[ "mtar_value" ], 1. )
		self.assertEqual( retp[ "mtar_unit" ], None )

	def test_retrieve_body_mass_onekg( self ):
		resp = self.make_obj( "mtar_value=1&mtar_unit=kg" )

		mass, retp = resp.retrieve_body_mass( "tar" )

		self.assertEqual( mass, 1. / resp.MASS_KG_MSOL )
		self.assertEqual( retp[ "mtar_value" ], 1. )
		self.assertEqual( retp[ "mtar_unit" ], "kg" )

	def test_retrieve_body_mass_implarge( self ):
		resp = self.make_obj( "mimp_value=2&mimp_unit=target" )

		mtar = 1. / resp.MASS_KG_MSOL
		mass, retp = resp.retrieve_body_mass( "imp", mtar )

		self.assertEqual( mass, None )
		self.assertEqual( retp[ "mimp_value" ], None )
		self.assertEqual( retp[ "mimp_unit" ], "target" )

	def test_retrieve_body_mass_imphalf( self ):
		resp = self.make_obj( "mimp_value=0.5&mimp_unit=target" )

		mtar = 1. / resp.MASS_KG_MSOL
		mass, retp = resp.retrieve_body_mass( "imp", mtar )

		self.assertEqual( mass, 0.5 / resp.MASS_KG_MSOL )
		self.assertEqual( retp[ "mimp_value" ], 0.5 )
		self.assertEqual( retp[ "mimp_unit" ], "target" )

	def test_retrieve_body_mass_impzero( self ):
		resp = self.make_obj( "mimp_value=0&mimp_unit=target" )

		mtar = 1. / resp.MASS_KG_MSOL
		mass, retp = resp.retrieve_body_mass( "imp", mtar )

		self.assertEqual( mass, None )
		self.assertEqual( retp[ "mimp_value" ], None )
		self.assertEqual( retp[ "mimp_unit" ], "target" )

	def test_retrieve_body_size_c2019model( self ):
		resp = self.make_obj( "" )

		model = "c2019"
		mtar = 1. / resp.MASS_MEARTH_MSOL

		radius, retp = resp.retrieve_body_size( "tar", mtar, model )

		self.assertEqual( radius, 0. )
		self.assertEqual( retp[ "rtar_type" ], "e2020" )
		self.assertEqual( retp[ "rtar_value" ], None )
		self.assertEqual( retp[ "rtar_unit" ], None )
		self.assertEqual( retp[ "dtar_value" ], None )
		self.assertEqual( retp[ "dtar_unit" ], None )

	def test_retrieve_body_size_mergerinvalid( self ):
		resp = self.make_obj( "" )

		model = "merger"
		mtar = 1. / resp.MASS_MEARTH_MSOL

		radius, retp = resp.retrieve_body_size( "tar", mtar, model )

		self.assertEqual( radius, None )
		self.assertEqual( retp[ "rtar_type" ], None )
		self.assertEqual( retp[ "rtar_value" ], None )
		self.assertEqual( retp[ "rtar_unit" ], None )
		self.assertEqual( retp[ "dtar_value" ], None )
		self.assertEqual( retp[ "dtar_unit" ], None )

	def test_retrieve_body_size_e2020user( self ):
		resp = self.make_obj( "rtar_type=e2020" )

		model = "merger"
		mtar = 1. / resp.MASS_MEARTH_MSOL

		radius, retp = resp.retrieve_body_size( "tar", mtar, model )

		self.assertEqual( radius, 0. )
		self.assertEqual( retp[ "rtar_type" ], "e2020" )
		self.assertEqual( retp[ "rtar_value" ], None )
		self.assertEqual( retp[ "rtar_unit" ], None )
		self.assertEqual( retp[ "dtar_value" ], None )
		self.assertEqual( retp[ "dtar_unit" ], None )

	def test_retrieve_body_size_radunitinv( self ):
		resp = self.make_obj( "rtar_type=rad&rtar_value=1&rtar_unit=venus" )

		model = "merger"
		mtar = 1. / resp.MASS_MEARTH_MSOL

		radius, retp = resp.retrieve_body_size( "tar", mtar, model )

		self.assertEqual( radius, None )
		self.assertEqual( retp[ "rtar_type" ], "rad" )
		self.assertEqual( retp[ "rtar_value" ], 1. )
		self.assertEqual( retp[ "rtar_unit" ], None )
		self.assertEqual( retp[ "dtar_value" ], None )
		self.assertEqual( retp[ "dtar_unit" ], None )

	def test_retrieve_body_size_radunit( self ):
		resp = self.make_obj( "rtar_type=rad&rtar_value=1&rtar_unit=earth" )

		model = "merger"
		mtar = 1. / resp.MASS_MEARTH_MSOL

		radius, retp = resp.retrieve_body_size( "tar", mtar, model )

		self.assertEqual( radius, 1. / resp.DIST_REARTH_AU )
		self.assertEqual( retp[ "rtar_type" ], "rad" )
		self.assertEqual( retp[ "rtar_value" ], 1. )
		self.assertEqual( retp[ "rtar_unit" ], "earth" )
		self.assertEqual( retp[ "dtar_value" ], None )
		self.assertEqual( retp[ "dtar_unit" ], None )

	def test_retrieve_body_size_dens( self ):
		resp = self.make_obj( "rtar_type=dens&dtar_value=1&dtar_unit=cgs" )

		model = "merger"
		mtar = 1. / resp.MASS_MEARTH_MSOL

		radius, retp = resp.retrieve_body_size( "tar", mtar, model )

		self.assertEqual( radius, 7.523625311879015e-05 )
		self.assertEqual( retp[ "rtar_type" ], "dens" )
		self.assertEqual( retp[ "rtar_value" ], None )
		self.assertEqual( retp[ "rtar_unit" ], None )
		self.assertEqual( retp[ "dtar_value" ], 1. )
		self.assertEqual( retp[ "dtar_unit" ], "cgs" )

if __name__ == '__main__':
	unittest.main()
