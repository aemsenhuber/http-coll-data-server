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
import hcds_responder_base

class SPHResponder( hcds_responder_base.BaseResponder ):
	def __init__( self, config ):
		hcds_responder_base.BaseResponder.__init__( self, config )

	def get_item_defs( self ):
		confdir = self.get_config( "dir" )
		conffile = self.get_config( "file" )

		items = None
		if not conffile is None:
			if not confdir is None:
				conffile = confdir + "/" + conffile

			try:
				items = yaml.load( open( conffile ), Loader = yaml.Loader )
			except FileNotFoundError:
				pass

		# Fall back to the configuration set in hcds_config.py
		if items is None:
			items = self.get_config( "items", {} )

		# If it was set, we add the directory path to all data files as well
		if not confdir is None:
			for key in items:
				items[ key ][ "file" ] = confdir + "/" + items[ key ][ "file" ]

		return items

	def num( self, val ):
		if math.isfinite( val ):
			return val
		else:
			return None

	def __call__( self ):
		"""
		Main entry point.
		"""

		sub = self.get_sub()
		items = self.get_item_defs()

		# The base URL lists all available items
		if sub is None or sub == "":
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
