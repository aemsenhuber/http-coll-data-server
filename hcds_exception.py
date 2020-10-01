# Exceptions for HTTP Collision Data Server (HCDS)
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

import json

class HCDSException( Exception ):
	'''
	Base exception with custom rendering in HTTP requests.
	'''
	def get_status( self ):
		return '500 Internal Server Error'

	def get_content_type( self ):
		return 'text/plain'

	def get_body( self ):
		return b'500 Internal Server Error'

class NotFound( HCDSException ):
	'''
	Exception that renders an HTTP 404 "Not Found" error page.
	'''

	def get_status( self ):
		return '404 Not Found'

	def get_content_type( self ):
		return 'text/plain'

	def get_body( self ):
		return b'404 Not Found'

class JSONBadRequest( HCDSException ):
	'''
	Exception for invalid or incomplete parameters given in the request.
	While this is an error, it returns a HTTP 200 "OK" response because the error is provided in the body of the response.
	This is needed to Ajax to be able to access the body of the response.
	'''

	def __init__( self, data ):
		HCDSException.__init__( self )
		self.data = data

	def get_status( self ):
		return '200 OK'

	def get_content_type( self ):
		return 'application/json'

	def get_body( self ):
		return bytes( json.dumps( self.data ), "utf-8" )
