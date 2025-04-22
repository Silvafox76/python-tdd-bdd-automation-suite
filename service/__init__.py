######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Package: service

This module creates and configures the Flask app and sets up logging and the SQL database
"""

import sys
from flask import Flask
from service import config
from service.common import log_handlers

# Create the Flask app
app = Flask(__name__)  # pylint: disable=invalid-name

# Load Configurations
app.config.from_object(config)

# Import routes and models AFTER the app is created
from service import routes, models  # noqa: F401, E402
from service.common import error_handlers, cli_commands  # noqa: F401, E402

# Set up logging for production environments
log_handlers.init_logging(app, "gunicorn.error")

# Log banner
app.logger.info("*" * 70)
app.logger.info("  P R O D U C T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info("*" * 70)

# Initialize the database
def initialize_service():
    """Initialize the service and database"""
    try:
        models.init_db(app)  # Create the SQLAlchemy tables
    except Exception as error:  # pylint: disable=broad-except
        app.logger.critical("%s: Cannot continue", error)
        sys.exit(4)  # Gunicorn expects exit code 4 to stop restarting the worker

    app.logger.info("Service initialized!")

initialize_service()
