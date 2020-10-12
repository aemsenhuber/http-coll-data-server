# HTTP Collision Data Server (HCDS) Responder for collresolve.
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

import io
import math
import json

import numpy
import matplotlib
matplotlib.use( "agg" )
import matplotlib.pyplot

import mpl_tune
import collresolve

import hcds_exception
import hcds_responder_base

class CollResponder( hcds_responder_base.BaseResponder ):
	def __init__( self, config ):
		hcds_responder_base.BaseResponder.__init__( self, config )

		# Unit conversion
		self.MASS_MJUP_MSOL = 1.3271244e+26 / 1.2668653e+23
		self.MASS_MEARTH_MSOL = 1.3271244e+26 / 3.986004e+20
		self.MASS_KG_MSOL = 1.3271244e+26 / 6.67408e-08 / 1.e3
		self.DIST_RJUP_AU = 1.495978707e+13 / math.pow( 7.1492e9**2 * 6.6854e9, 1. / 3. )
		self.DIST_REARTH_AU = 1.495978707e+13 / math.pow( 6.3781e8**2 * 6.3568e9, 1. / 3. )
		self.DIST_M_AU = 1.495978707e+11
		self.VEL_KMS_AUD = 1.495978707e+8 / 86400.

		# collresolve's configuration object
		self.conf = collresolve.Conf()
		collresolve.conf_unit_msun_au_day( self.conf )
		collresolve.conf_model( self.conf, collresolve.MODEL_C2019 )

	def retrieve_body_mass( self, body, target = False ):
		value = self.parse_float_query( "m" + body + "_value" )
		unit = self.parse_list_query( "m" + body + "_unit", [ "jupiter", "earth", "mars", "moon", "kg" ] if target is False else [ "target", "jupiter", "earth", "mars", "moon", "kg" ] )

		# Obtain the numerical value of the target's mass in Solar masses
		if value is None or unit is None:
			num = None
		else:
			if unit == "kg":
				num = value / self.MASS_KG_MSOL
			elif unit == "moon":
				num = value * 7.342e22 / self.MASS_KG_MSOL
			elif unit == "mars":
				num = value * 6.4171e23 / self.MASS_KG_MSOL
			elif unit == "earth":
				num = value / self.MASS_MEARTH_MSOL
			elif unit == "jupiter":
				num = value / self.MASS_MJUP_MSOL
			elif unit == "target":
				if target is None:
					num = None
				else:
					num = value * target
			else:
				num = None
				unit = None

			if not num is None:
				if num <= 0.:
					num = None
					value = None
				elif not ( target is False or target is None ) and num > target:
					num = None
					value = None

		return num, { "m" + body + "_value": value, "m" + body + "_unit": unit }

	def retrieve_body_size( self, body, mass, model ):
		size_type = self.parse_list_query( "r" + body + "_type", [ "rad", "dens", "e2020" ] )
		rad_value = self.parse_float_query( "r" + body + "_value" )
		rad_unit = self.parse_list_query( "r" + body + "_unit", [ "m", "km", "moon", "mars", "earth", "jupiter" ] )
		dens_value = self.parse_float_query( "d" + body + "_value" )
		dens_unit = self.parse_list_query( "d" + body + "_unit", [ "cgs", "si" ] )

		# Obtain the numerical value of the radius
		if model == "c2019" or size_type == "e2020":
			# This is a special case where the radius will be computed later.
			# We force this for the collision model "c2019" for consistency.
			size = 0.
			size_type = "e2020"
		elif size_type == "rad":
			# Target radius is directly provided by the caller
			if rad_unit == "m":
				size = rad_value / self.DIST_M_AU
			elif rad_unit == "km":
				size = rad_value * 1.e3 / self.DIST_M_AU
			elif rad_unit == "moon":
				size = rad_value * 1.7371e5 / self.DIST_M_AU
			elif rad_unit == "mars":
				size = rad_value * 3.396e6 / self.DIST_M_AU
			elif rad_unit == "earth":
				size = rad_value / self.DIST_REARTH_AU
			elif rad_unit == "jupiter":
				size = rad_value / self.DIST_RJUP_AU
			else:
				size = None
				rad_unit = None

			# Check that radius is positive
			if not size is None and size <= 0.:
				size = None
				rad_value = None
		elif size_type == "dens":
			# Target radius is directly provided by the caller
			if dens_unit == "cgs":
				dens = dens_value * 1.e3
			elif dens_unit == "si":
				dens = dens_value
			else:
				dens = None
				dens_unit = None

			# Check that density is strictly positive
			if not dens is None and dens <= 0.:
				dens = None
				dens_value = None

			# Convert mass and density into radius
			if mass is None or dens is None:
				size = None
			else:
				size = math.pow( 3. / 4. / math.pi * ( mass * self.MASS_KG_MSOL ) / dens, 1. / 3. ) / 1.495978707e+11
		else:
			size = None

		return size, { "r" + body + "_type": size_type, "r" + body + "_value": rad_value, "r" + body + "_unit": rad_unit, "d" + body + "_value": dens_value, "d" + body + "_unit": dens_unit }

	def retrieve_params( self, items, model = None ):
		'''
		Retrieve all the needed parameters for the call, as set by the "items" parameter.
		'''

		# Values to be used by the program
		values = {}
		# Values to be returned to the caller
		response = {}

		if "model" in items:
			model = self.parse_list_query( "model", [ "merge", "ls2012", "sl2012", "c2019" ] )
			values[ "model" ] = model
			response[ "model" ] = model

		if "mtar" in items or "tar" in items:
			mtar, mtar_params = self.retrieve_body_mass( "tar" )
			values[ "mtar" ] = mtar
			response.update( mtar_params )
		else:
			mtar = False

		if "mimp" in items or "imp" in items:
			mimp, mimp_params = self.retrieve_body_mass( "imp", mtar )
			values[ "mimp" ] = mimp
			response.update( mimp_params )
		else:
			mimp = False

		if "rtar" in items or "tar" in items:
			rtar, rtar_params = self.retrieve_body_size( "tar", mtar, model )
			values[ "rtar" ] = rtar
			response.update( rtar_params )

		if "rimp" in items or "imp" in items:
			rimp, rimp_params = self.retrieve_body_size( "imp", mtar, model )
			values[ "rimp" ] = rimp
			response.update( rimp_params )

		if "vel" in items:
			vel_value = self.parse_float_query( "vel_value" )
			vel_unit = self.parse_list_query( "vel_unit", [ "escape", "kms" ] )

			# Obtain the numerical value of the impact velocity
			# In case of a value relative to the mutual escape velocity of the bodies, this only retrives the factor. The actual escape velocity will be computed later on.
			if vel_value is None or vel_unit is None:
				vel = None
			else:
				if vel_unit == "escape":
					vel = vel_value
				else:
					vel = vel_value / self.VEL_KMS_AUD
				if vel <= 0.:
					vel = None
					vel_value = None

			values[ "vel" ] = vel
			response[ "vel_value" ] = vel_value
			response[ "vel_unit" ] = vel_unit

		if "angle" in items:
			angle_value = self.parse_float_query( "angle_value" )

			# Check that the impact angle is within boundaries
			if not angle_value is None and ( angle_value < 0. or angle_value > 90. ):
				angle_value = None

			values[ "angle" ] = angle_value
			response[ "angle_value" ] = angle_value

		for key in values:
			if values[ key ] is None:
				raise hcds_exception.JSONBadRequest( response )

		if "tar" in items:
			# Create the target object
			if response[ "rtar_type" ] == "e2020":
				collresolve.conf_model( self.conf, collresolve.MODEL_C2019 )
				values[ "tar" ] = collresolve.Body( mass = values[ "mtar" ] )
				collresolve.body_radius( self.conf, values[ "tar" ] )
			else:
				values[ "tar" ] = collresolve.Body( mass = values[ "mtar" ], radius = values[ "rtar" ] )

			# Add the true radius to the response
			response[ "rtar" ] = values[ "tar" ].radius * self.DIST_REARTH_AU

		if "imp" in items:
			# Create the impactor object
			if response[ "rimp_type" ] == "e2020":
				collresolve.conf_model( self.conf, collresolve.MODEL_C2019 )
				values[ "imp" ] = collresolve.Body( mass = values[ "mimp" ] )
				collresolve.body_radius( self.conf, values[ "imp" ] )
			else:
				values[ "imp" ] = collresolve.Body( mass = values[ "mimp" ], radius = values[ "rimp" ] )

			# Add the true radius to the response
			response[ "rimp" ] = values[ "imp" ].radius * self.DIST_REARTH_AU

		if "model" in items:
			# Apply the correct model to the collresolve configuration
			# This needs to be done *after* setting-up the bodies, otherwise the model may be changed!
			if values[ "model" ] == "c2019":
				collresolve.conf_model( self.conf, collresolve.MODEL_C2019 )
			elif values[ "model" ] == "sl2012":
				collresolve.conf_model( self.conf, collresolve.MODEL_SL2012 )
			elif values[ "model" ] == "ls2012":
				collresolve.conf_model( self.conf, collresolve.MODEL_LS2012 )
			else:
				collresolve.conf_model( self.conf, collresolve.MODEL_PERFECT_MERGE )

		return values, response

	def get_types( self ):
		format = self.parse_list_query( "format", [ "jsoncheck", "jsondata", "jsonsvg", "svg", "pdf", "png", "jpg" ] )

		if format == "jsondata":
			return { "ctype": "application/json", "data": "json", "image": None }
		if not format is None and format[ 0:4 ] == "json" and format != "jsoncheck":
			return { "ctype": "application/json", "data": "json", "image": format[ 4: ] }
		elif format == "svg":
			return { "ctype": "image/svg+xml", "data": "image", "image": "svg" }
		elif format == "pdf":
			return { "ctype": "application/pdf", "data": "image", "image": "pdf" }
		elif format == "png":
			return { "ctype": "image/png", "data": "image", "image": "png" }
		elif format == "jpg":
			return { "ctype": "image/jpeg", "data": "image", "image": "jpg" }
		else:
			return { "ctype": "application/json", "data": "check", "image": None }

	def __call__( self ):
		'''
		Main entry point of the module.
		'''

		sub = self.get_sub()

		if sub == "single" or sub == "single/":
			return self.single()
		elif sub == "grid" or sub == "grid/":
			return self.grid()
		else:
			raise hcds_exception.NotFound

	def single( self ):
		'''
		Handle a request to obtain the outcome of one precise collision.
		'''

		values, response = self.retrieve_params( [ "model", "tar", "imp", "vel", "angle" ] )

		vel = values[ "vel" ]
		if response[ "vel_unit" ] == "escape":
			vel *= collresolve.escape_velocity( self.conf, values[ "tar" ], values[ "imp" ] )

		collresolve.setup( self.conf, values[ "tar" ], values[ "imp" ], vel, math.radians( values[ "angle" ] ) )

		res, regime = collresolve.resolve( self.conf, values[ "tar" ], values[ "imp" ], 2, 1 )

		response[ "regime" ] = collresolve.regime_desc( regime )

		response[ "acclr" ] = ( res[ 0 ].mass - values[ "tar" ].mass ) / values[ "imp" ].mass
		response[ "accsr" ] = ( res[ 1 ].mass - values[ "imp" ].mass ) / values[ "imp" ].mass
		response[ "acctr" ] = ( res[ 2 ].mass ) / values[ "imp" ].mass

		self.start( '200 OK', [ ( "Content-Type", "application/json" ) ] )
		self.add_output( bytes( json.dumps( response ), "utf-8" ) )

	def grid( self ):
		'''
		Handle a request to obtain a map of outcomes.
		'''

		# First, we parse all the input parameters from the query string and validate the ones given as string against the list of allowed values
		formats = self.get_types()

		values, response = self.retrieve_params( [ "model", "tar", "imp" ] )

		if formats[ "data" ] == "check":
			response[ "check" ] = True

			self.start( "200 OK", [ ( "Content-Type", formats[ "ctype" ] ) ] )
			self.add_output( bytes( json.dumps( response ), "utf-8" ) )

			return

		esc = collresolve.escape_velocity( self.conf, values[ "tar" ], values[ "imp" ] )

		quant = self.parse_list_query( "quant", [ "regime", "acclr", "accsr", "acctr" ] )
		if quant is None:
			quant = "regime"

		xmin = 0.
		xmax = 90.
		xscale = "linear"
		xname = "\\theta_{coll}~[deg]"
		nx = 91
		x = numpy.linspace( xmin, xmax, nx )
		xt = [ 0., 15., 30., 45., 60., 75., 90. ]
		xl = None

		ymin = 0.99
		ymax = 4.01
		yscale = "linear"
		yname = "v_{coll}/v_{esc}"
		ny = 91
		y = numpy.linspace( ymin, ymax, ny )
		yt = None
		yl = None

		z = numpy.zeros( ( ny, nx ) )

		for i in range( nx ):
			ang = x[ i ]

			for j in range( ny ):
				vel = esc * y[ j ]

				collresolve.setup( self.conf, values[ "tar" ], values[ "imp" ], vel, math.radians( ang ) )

				try:
					res, regime = collresolve.resolve( self.conf, values[ "tar" ], values[ "imp" ], 2, 1 )

					if quant == "acclr":
						val = ( res[ 0 ].mass - values[ "tar" ].mass ) / values[ "imp" ].mass
					elif quant == "accsr":
						if regime != 5:
							val = -1.1
						else:
							val = res[ 1 ].mass / values[ "imp" ].mass - 1.
					elif quant == "acctr":
						val = res[ 2 ].mass / values[ "imp" ].mass
					else:
						val = regime

					z[ j, i ] = val
				except:
					z[ j, i ] = 0.

		buffer = None

		if formats[ "image" ] is None:
			response[ "vels" ] = y.tolist()
			response[ "angs" ] = x.tolist()
			response[ "vals" ] = z.tolist()
		else:
			# Matplotlib

			matplotlib.rc( "font", family = "serif" )

			if self.get_config( "usetex" ):
				matplotlib.rc( "text", usetex = True )
				matplotlib.rc( "text.latex", preamble = "\\usepackage{amsmath}\n\\usepackage{wasysym}\n\\usepackage{mathptmx}" )

			figtext = mpl_tune.FigText( size = "large", color = "black", tex = self.get_config( "usetex" ) )

			figsize = mpl_tune.FigSize()
			figsize.set_size_h( 5.0, mpl_tune.FigSize.SIZE_NO_CBAR )
			figsize.set_size_v( 5.0, mpl_tune.FigSize.SIZE_NO_CBAR )
			figsize.set_margin_left( 0.52 )
			figsize.set_margin_bottom( 0.52 )
			figsize.set_margin_right( 0.08 )
			figsize.set_margin_top( 0.08 )

			# Color bar
			figsize.set_cbar_loc( "right" )
			figsize.set_cbar_width( 0.1 )
			figsize.set_cbar_pad( 0.75 )

			fig = matplotlib.pyplot.figure( **figsize.get_figure_args() )
			fig.subplots_adjust( **figsize.get_subplots_args() )

			ax = fig.add_subplot( 1, 1, 1 )

			if quant == "regime":
				vmin = 0.5
				vmax = 5.5
				n = [ 0.5, 1.5, 2.5, 3.5, 4.5, 5.5 ]
			else:
				vmin = -1.
				vmax = 1.
				n = [ -100., -1.05, -0.95, -0.85, -0.75, -0.65, -0.55, -0.45, -0.35, -0.25, -0.15, -0.05, 0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.05, 100. ]

			cmap = matplotlib.cm.get_cmap( "RdBu" )
			cmap.set_under( "black" )
			cmap.set_bad( "black" )

			ax.patch.set_facecolor( "white" )
			ax.patch.set_edgecolor( "white" )
			ax.contourf( x, y, z, n, cmap = cmap, vmin = vmin, vmax = vmax )

			if figsize.has_cbar():
				cax = fig.add_axes( figsize.get_cbar_ax_spec() )
				if quant == "regime":
					kwargs = { "boundaries": [ 0.5, 1.5, 2.5, 3.5, 4.5, 5.5 ], "values": [ 1., 2., 3., 4., 5. ] }
				else:
					bounds = [ v for v in n ]
					bounds.pop()
					bounds.pop( 0 )
					kwargs = { "boundaries": bounds }
				norm = matplotlib.colors.Normalize( vmin = vmin, vmax = vmax )
				mappabble = matplotlib.cm.ScalarMappable( norm, cmap )

				cb = fig.colorbar( mappabble, orientation = figsize.get_cbar_orientation(), cax = cax, **kwargs, filled = True )

			if xscale == "log":
				ax.set_xscale( "log" )
				ax.set_xlim( 10 ** xmin, 10 ** xmax )
			else:
				ax.set_xlim( xmin, xmax )

			if yscale == "log":
				ax.set_yscale( "log" )
				ax.set_ylim( 10 ** ymin, 10 ** ymax )
			else:
				ax.set_ylim( ymin, ymax )

			ax.set_xlabel( "$\\mathrm{" + xname + "}$", **figtext.get_text_args() )
			if not xt is None:
				ax.set_xticks( xt )
				ax.set_xticks( [], minor = True )
			if not xl is None:
				ax.set_xticklabels( xl, **figtext.get_text_args() )

			ax.set_ylabel( "$\\mathrm{" + yname + "}$", **figtext.get_text_args() )
			if not yt is None:
				ax.set_yticks( yt )
				ax.set_yticks( [], minor = True )
			if not yl is None:
				ax.set_yticklabels( yl, **figtext.get_text_args() )

			if figsize.has_cbar():
				if quant == "acclr":
					cb.set_label( "Accretion efficiency of largest remnant", **figtext.get_text_args() )
				elif quant == "accsr":
					cb.set_label( "Accretion efficiency of second remnant", **figtext.get_text_args() )
				elif quant == "acctr":
					cb.set_label( "Accretion efficiency of debris", **figtext.get_text_args() )
				else:
					cb.set_label( "Collision regime", **figtext.get_text_args() )

				if quant == "regime":
					cb.set_ticks( [ 1., 2., 3., 4., 5. ] )
					cb.set_ticklabels( [ "Accretion", "Erosion", "Super cat.", "Graze and Merge", "Hit and Run" ] )
				else:
					cb.set_ticks( [ -1., -0.5, 0., 0.5, 1. ] )

				figtext.set_cbar( cb )

			figtext.set_axes( ax )

			if formats[ "data" ] == "image":
				buffer = io.BytesIO()
			else:
				buffer = io.StringIO()

			fig.savefig( buffer, dpi = 250, format = formats[ "image" ], facecolor = "none", edgecolor = "none" )

			if formats[ "data" ] != "image":
				response[ "image" ] = buffer.getvalue()

			matplotlib.pyplot.close( fig )

		self.start( "200 OK", [ ( "Content-Type", formats[ "ctype" ] ) ] )
		if formats[ "data" ] == "image":
			self.add_output( buffer.getvalue() )
		else:
			self.add_output( bytes( json.dumps( response ), "utf-8" ) )
