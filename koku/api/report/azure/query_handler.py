#
# Copyright 2019 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Azure Query Handling for Reports."""
from api.report.aws.query_handler import AWSReportQueryHandler
from api.report.azure.provider_map import AzureProviderMap

EXPORT_COLUMNS = []


class AzureReportQueryHandler(AWSReportQueryHandler):
    """Handles report queries and responses for AWS."""
