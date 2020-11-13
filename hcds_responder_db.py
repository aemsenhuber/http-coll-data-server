# HTTP Collision Data Server (HCDS) Responder for collision database.
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

import yaml
import maexpa

import hcds_exception
import hcds_responder_sph

class DBResponder( hcds_responder_sph.SPHResponder ):
	def compute_item( self, config, sub ):
		h5file = tables.open_file( config[ "file" ] )

		if sub is None or sub == "":
			group = h5file.root.base

			defs = config[ "base_fields" ]

			get_data = lambda name: numpy.asarray( getattr( group, name )[ ... ] )

			data = [ maexpa.Expression( item[ "data" ], var = get_data )() for item in defs ]

			items = []
			for i in range( data[ 0 ].shape[ 0 ] ):
				entry = {}
				for j, item in enumerate( defs ):
					if str( data[ j ].dtype ) == "int64":
						entry[ item[ "name" ] ] = int( data[ j ][ i ] )
					else:
						entry[ item[ "name" ] ] = data[ j ][ i ]
				items.append( entry )

			h5file.close()

			fields = []
			for item in defs:
				fields.append( { "name": item[ "name" ], "desc": item[ "desc" ], "format": item[ "format" ] } )

			response = {
				"fields": fields,
				"series": items,
			}

			self.start( "200 OK", [ ( "Content-Type", "application/json" ) ] )
			self.add_output( bytes( json.dumps( response ), "utf-8" ) )
			return

		try:
			try:
				num = int( sub )
				group = h5file.root.__getattr__( "sim_{:03d}".format( num ) )
			except:
				raise hcds_exception.NotFound

			defs = config[ "fields" ]

			get_data = lambda name: numpy.asarray( getattr( group, name )[ ... ] )

			data = [ maexpa.Expression( item[ "data" ], var = get_data )() for item in defs ]

			series = []
			for i in range( len( data[ 0 ] ) ):
				point = {}
				for j, field in enumerate( defs ):
					point[ field[ "name" ] ] = self.num( data[ j ][ i ] )
				series.append( point )
		finally:
			h5file.close()

		response = {
			"plots": config[ "plots" ],
			"series": series,
		}

		self.start( "200 OK", [ ( "Content-Type", "application/json" ) ] )
		self.add_output( bytes( json.dumps( response ), "utf-8" ) )
