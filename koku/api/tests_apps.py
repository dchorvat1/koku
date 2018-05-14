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
"""Test the API apps module."""
from django.apps import apps
from django.contrib.auth.models import User
from django.test import TestCase

from koku.env import ENVIRONMENT


class AppsModelTest(TestCase):
    """Tests against the apps functions."""

    def tearDown(self):
        """Tear down the app tests."""
        User.objects.all().delete()

    def test_check_service_admin(self):
        """Test the check and create of service admin."""
        User.objects.all().delete()
        service_email = ENVIRONMENT.get_value('SERVICE_ADMIN_EMAIL',
                                              default='admin@example.com')
        self.assertTrue(User.objects.filter(
            email=service_email).count() == 0)
        api_config = apps.get_app_config('api')
        api_config.check_and_create_service_admin()
        self.assertTrue(User.objects.filter(
            email=service_email).count() != 0)

    def test_check_service_admin_exists(self):
        """Test the check and proceed of the service admin."""
        User.objects.all().delete()
        service_email = ENVIRONMENT.get_value('SERVICE_ADMIN_EMAIL',
                                              default='admin@example.com')
        service_user = ENVIRONMENT.get_value('SERVICE_ADMIN_USER',
                                             default='admin')
        service_pass = ENVIRONMENT.get_value('SERVICE_ADMIN_PASSWORD',
                                             default='pass')

        User.objects.create_superuser(service_user,
                                      service_email,
                                      service_pass)
        self.assertTrue(User.objects.filter(
            email=service_email).count() == 1)
        api_config = apps.get_app_config('api')
        api_config.check_and_create_service_admin()
        self.assertTrue(User.objects.filter(
            email=service_email).count() != 0)

    def test_create_service_admin(self):
        """Test the creation of the service admin."""
        service_email = ENVIRONMENT.get_value('SERVICE_ADMIN_EMAIL',
                                              default='admin@example.com')
        api_config = apps.get_app_config('api')
        api_config.create_service_admin(service_email)
        self.assertTrue(User.objects.filter(
            email=service_email).count() != 0)
