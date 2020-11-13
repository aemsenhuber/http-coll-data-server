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

import yaml
import maexpa

import hcds_exception
import hcds_responder_sph

class SetResponder( hcds_responder_sph.SPHResponder ):
	def compute_item( self, config, sub ):
		# Disallow subpages
		if not ( sub is None or sub == "" ):
			raise hcds_exception.NotFound

		defs = config[ "fields" ]
		h5file = tables.open_file( config[ "file" ] )

		data = []
		labels = []

		try:
			for n in range( 1000 ):
				try:
					group = h5file.root.__getattr__( "file_{:03d}".format( n ) )
				except:
					continue

				get_data = lambda name: numpy.asarray( getattr( group, name )[ ... ] )

				sets = [ maexpa.Expression( item[ "data" ], var = get_data )() for item in defs ]

				items = []
				for i in range( len( sets[ 0 ] ) ):
					items.append( [ self.num( dset[ i ] ) for dset in sets ] )

				data.append( items )
				labels.append( group._v_attrs[ "desc" ] )
		finally:
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
