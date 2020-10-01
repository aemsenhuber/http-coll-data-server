# HTTP Collision Data Server (HCDS) Responder for SPH simulation data.
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

import math
import json

import numpy
import tables

import hcds_exception
import hcds_responder_base

class SPHResponder( hcds_responder_base.BaseResponder ):
	def __init__( self, config ):
		hcds_responder_base.BaseResponder.__init__( self, config )

	def split_text( self, line ):
		size = len( line )
		num = 1 + ( size - 10 ) // 15
		items = [ line[ :10 ].strip() ]
		for i in range( 1, num ):
			items.append( line[ 15 * i - 5 : 15 * ( i + 1 ) - 5 ].strip() )
		return items

	def num( self, val ):
		if math.isfinite( val ):
			return val
		else:
			return None

	def __call__( self ):
		sub = self.get_sub()
		items = self.get_config( "items" )

		if sub == "" or sub == "/":
			response = []
			for key in items:
				response.append( { "name": key, "desc": items[ key ][ "desc" ] } )

			self.start( "200 OK", [ ( "Content-Type", "application/json" ) ] )
			self.add_output( bytes( json.dumps( response ), "utf-8" ) )
			return

		for key in items:
			if sub == key or sub == key + "/":
				self.compute_item( items[ key ] )
				return

		raise hcds_exception.NotFound

	def compute_item( self, config ):
		defs = config[ "fields" ]
		h5file = tables.open_file( config[ "file" ] )

		data = []
		labels = []
		for n in range( 1000 ):
			try:
				group = h5file.root.__getattr__( "file_{:03d}".format( n ) )
			except:
				continue

			sets = []
			for item in defs:
				values = group.__getattr__( item[ "key" ] )[ : ]
				if "factor" in item:
					values = [ _ * item[ "factor" ] for _ in values ]
				sets.append( values )

			items = []
			for i in range( len( sets[ 0 ] ) ):
				items.append( [ self.num( dset[ i ] ) for dset in sets ] )

			data.append( items )
			labels.append( group._v_attrs[ "desc" ] )

		h5file.close()

		response = {
			"value": [ item[ "value" ] for item in defs ],
			"unit": [ item[ "unit" ] for item in defs ],
			"short": [ ( item[ "short" ] if "short" in item else item[ "value" ] ) for item in defs ],
			"series": data,
			"label": labels,
		}

		self.start( "200 OK", [ ( "Content-Type", "application/json" ) ] )
		self.add_output( bytes( json.dumps( response ), "utf-8" ) )
