#
# Copyright 2018 Red Hat, Inc.
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

"""Test the AuthDBAccessor utility object."""

from masu.database.auth_db_accessor import AuthDBAccessor
from tests import MasuTestCase


class AuthDBAccessorTest(MasuTestCase):
    """Test Cases for the AuthDBAccessor object."""

    def setUp(self):
        pass

    def test_initializer(self):
        '''Test Initializer'''
        auth_id = '1'
        accessor = AuthDBAccessor(auth_id)
        self.assertIsNotNone(accessor._session)
        self.assertTrue(accessor.does_db_entry_exist())

    def test_get_name(self):
        """Test name getter."""
        auth_id = '1'
        accessor = AuthDBAccessor(auth_id)
        self.assertEqual('Test Customer', accessor.get_name())
