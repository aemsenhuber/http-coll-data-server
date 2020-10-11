# Default configuration for HTTP Collision Data Server (HCDS)
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


# The network address to bind the server socket to
# Use "localhost" to restrict access from the local machine.
SERVER_ADDRESS = ""

# The TCP port to listen to
SERVER_PORT = 9099

# The base path for the API. Do not forget the trailing "/"!
# This the path that the front-end web server will redirect request to this back-end.
BASE_PATH = "/data/"

# Path map to modules and their configuration.
# Available modules are:
# - coll: The following item is available:
#         - usetex: Boolean to indicate whether to use LaTeX for text formatting
# - sph: One single key for configuration: items.
#        This key one dictionary of available datasets.
#        Each dataset is again a dictionary of three items:
#        - file: Path to HDF5 file containing the data
#        - desc: Human-reable description of the dataset
#        - fields: Array of fields to retrieve from the file and send to the caller. Each item here is dictionary with the following keys:
#          - data: Expression to compute the values; it is a mathematical expression parsed by MaExPa with the fields in the dataset available as variables
#          - value: Human-readable description of the field
#          - unit: Human-readable description of the unit of the data
#          - short: Short name of the field; optional, if not set, the "value" key will be used instead
MODS = {
	"coll": ( "coll", {
		"usetex": False,
	} ),
}

# List of hosts from which to allow cross-domain requests.
# This is useful during development when this server is not at the same address as the one providing the user interface.
CORS_ORIGINS = []
