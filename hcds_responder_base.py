# HTTP Collision Data Server (HCDS) base classes for services.
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
import urllib.parse

import hcds_config

class BaseResponder( object ):
	def __init__( self, config ):
		self.config = config
		self.clean()

	def clean( self ):
		'''
		Clean the object as preparation for a new request.
		'''

		self.environ = None
		self.start_response = None
		self.url = None
		self.query = None
		self.sub = None
		self.out = []

	def get_config( self, key, default = None ):
		'''
		Retrieve a configuration item.
		- key: Name of the item to access
		- default: default value of the item is not set in the configuration
		'''

		if key in self.config:
			return self.config[ key ]
		else:
			return default

	def set_request( self, environ, start_response ):
		'''
		Set the WSGI arguments to start a new request.
		- environ: WSGI environment
		- start_response: WSGI callback to start the response
		'''
		self.environ = environ
		self.start_response = start_response

	def set_url( self, url, sub ):
		'''
		Set the full request URL and the subpath of this module.
		- url: urllib.parse.ParseResult object
		- sub: subpath of the request URI of this module
		'''
		self.url = url
		self.sub = sub
		self.set_query( url.query )

	def set_query( self, query ):
		'''
		Analyse and save the query string portion of the URL.
		This is separate from set_url() so that it can be called by unit tests.

		- query: The query part of the URL
		'''

		self.query = urllib.parse.parse_qs( query )

	def get_env( self, key, default = None ):
		'''
		Retrieve a configuration item.
		- key: Name of the item to access
		- default: default value of the item is not set in the configuration
		'''

		if self.environ is None:
			raise Exception( "BaseResponder.get_env() called without request set." )

		if key in self.environ:
			return self.environ[ key ]
		else:
			return default

	def get_param( self, key, default = None ):
		'''
		Retrieve a query parameter.
		- key: Name of the parameter to access
		- default: default value of the item is not set in the configuration
		'''

		if self.query is None:
			raise Exception( "BaseResponder.get_env() called without request set." )

		if key in self.query and len( self.query[ key ] ):
			return self.query[ key ][ 0 ]
		else:
			return default

	def parse_float_query( self, name ):
		'''
		Retrieve a parameter passed in the URL query string as a floating-point number.
		This will sanitize the input to insure that the number is valid and finite.
		In case the parameter isn't provided or invalid, None is returned.

		- name: Name of the parameter to retrive
		'''

		value = self.query.get( name )
		if value is None:
			return value

		try:
			res = float( value[ 0 ] )
			if math.isfinite( res ):
				return res
			else:
				return None
		except:
			return None

	def parse_list_query( self, name, values ):
		'''
		Retrieve a parameter passed in the URL query string from a list of possible values.
		In case the parameter isn't provided or not in the list of allowed values, None is returned.

		- name: Name of the parameter to retrive
		- values: list of allowed values for the parameter
		'''

		value = self.query.get( name )
		if value is None:
			return value

		if value[ 0 ] in values:
			return value[ 0 ]
		else:
			return None

	def get_sub( self ):
		'''
		Get the subpath of the requested URI from this module.
		'''

		return self.sub

	def start( self, status, headers ):
		'''
		Start the reponse.
		Parameters are the same as for the callback in WSGI interface.
		'''

		additional = []
		for origin in hcds_config.CORS_ORIGINS:
			if origin == "*" or origin == self.get_env( "HTTP_ORIGIN" ):
				additional.append( ( "Access-Control-Allow-Origin", origin ) )
				break

		self.start_response( status, headers + additional )

	def add_output( self, out ):
		'''
		Add one item to the output.

		- out: Item to add, should be an instance of bytes()
		'''

		self.out.append( out )

	def get_output( self ):
		return self.out

	def __call__( self ):
		raise NotImplemented


class ErrorResponder( BaseResponder ):
	'''
	Simple responder to show an exception.
	'''

	def __init__( self, config, exception ):
		BaseResponder.__init__( self, config )
		self.exception = exception

	def __call__( self ):
		self.start( self.exception.get_status(), [ ( "Content-Type", self.exception.get_content_type() ) ] )
		self.add_output( self.exception.get_body() )

