#!/usr/bin/env python3
#
# Main entry point for HTTP Collision Data Server (HCDS)
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

import urllib.parse
import wsgiref.simple_server

import hcds_config
import hcds_exception
import hcds_responder_base

responder_cache = {}

def get_responder( path ):
	'''
	Get a responder for the given path component.

	- path: The path for which to obtain a hcds_responder_base.BaseResponder object
	'''

	if not path in responder_cache:
		if not path in hcds_config.MODS:
			raise hcds_exception.NotFound

		name, config = hcds_config.MODS[ path ]

		if name == "base":
			# That's just for testing; it should not be used as a real case
			responder_cache[ path ] = hcds_responder_base.BaseResponder( config )
		elif name == "coll":
			import hcds_responder_coll
			responder_cache[ path ] = hcds_responder_coll.CollResponder( config )
		elif name == "sph":
			import hcds_responder_set
			responder_cache[ path ] = hcds_responder_set.SetResponder( config )
		elif name == "db":
			import hcds_responder_db
			responder_cache[ path ] = hcds_responder_db.DBResponder( config )
		else:
			raise hcds_exception.NotFound

	return responder_cache[ path ]

def hcds_app( environ, respond ):
	'''
	Main WSGI entry point for the package.
	'''

	try:
		url = urllib.parse.urlparse( wsgiref.util.request_uri( environ ) )

		path = url.path
		if not path.startswith( hcds_config.BASE_PATH ):
			raise hcds_exception.NotFound

		path = path[ len( hcds_config.BASE_PATH ) : ]
		next_div = path.find( "/" )
		if next_div < 0:
			base = path
			sub = None
		else:
			base = path[ : next_div ]
			sub = path[ next_div + 1 : ]

		module = get_responder( base )
		module.set_request( environ, respond )
		module.set_url( url, sub )
		module()
		out = module.get_output()
		module.clean()

		return out
	except hcds_exception.HCDSException as ex:
		error = hcds_responder_base.ErrorResponder( {}, ex )

		error.set_request( environ, respond )
		error.set_url( url, None )

		error()

		return error.get_output()


if __name__ == '__main__':
	server = wsgiref.simple_server.make_server( hcds_config.SERVER_ADDRESS, hcds_config.SERVER_PORT, hcds_app )
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		server.server_close()
