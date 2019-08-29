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

"""Test the ReportDBAccessor utility object."""
import datetime
from decimal import Decimal
import types
import random

import psycopg2
from sqlalchemy.orm.query import Query

from masu.database.report_db_accessor import ReportDBAccessor, ReportSchema
from masu.database.reporting_common_db_accessor import ReportingCommonDBAccessor
from tests import MasuTestCase
from tests.database.helpers import ReportObjectCreator

COST_ENTRY_TABLE = 'reporting_awscostentry'
LINE_ITEM_TABLE = 'reporting_awscostentrylineitem'
REPORT_TABLES = (
    'reporting_awscostentrybill',
    'reporting_awscostentryproduct',
    'reporting_awscostentrypricing',
    'reporting_awscostentryreservation',
)

class ReportSchemaTest(MasuTestCase):
    """Test Cases for the ReportingCommonDBAccessor object."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with required objects."""
        cls.common_accessor = ReportingCommonDBAccessor()
        cls.column_map = cls.common_accessor.column_map
        cls.accessor = ReportDBAccessor(
            schema='testcustomer',
            column_map=cls.column_map
        )

    def test_init(self):
        """Test the initializer."""
        tables = self.accessor.get_base().classes
        report_schema = ReportSchema(tables, self.column_map)

        for table_name in REPORT_TABLES:
            self.assertIsNotNone(getattr(report_schema, table_name))
        self.assertIsNotNone(getattr(report_schema, COST_ENTRY_TABLE))
        self.assertIsNotNone(getattr(report_schema, LINE_ITEM_TABLE))
        self.assertNotEqual(report_schema.column_types, {})

    def test_get_reporting_tables(self):
        """Test that the report schema is populated with a column map."""
        tables = self.accessor.get_base().classes
        report_schema = ReportSchema(tables, self.column_map)

        report_schema._set_reporting_tables(
            tables,
            self.accessor.column_map
        )

        for table in REPORT_TABLES:
            self.assertIsNotNone(getattr(report_schema, table))

        self.assertTrue(hasattr(report_schema, 'column_types'))

        column_types = report_schema.column_types

        for table in REPORT_TABLES:
            self.assertIn(table, column_types)

        table_types = column_types[random.choice(REPORT_TABLES)]

        python_types = list(types.__builtins__.values())
        python_types.extend([datetime.datetime, Decimal])

        for table_type in table_types.values():
            self.assertIn(table_type, python_types)


class ReportDBAccessorTest(MasuTestCase):
    """Test Cases for the ReportingCommonDBAccessor object."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with required objects."""
        cls.common_accessor = ReportingCommonDBAccessor()
        cls.column_map = cls.common_accessor.column_map
        cls.accessor = ReportDBAccessor(
            schema='testcustomer',
            column_map=cls.column_map
        )
        cls.report_schema = cls.accessor.report_schema
        cls.creator = ReportObjectCreator(
            cls.accessor,
            cls.column_map,
            cls.report_schema.column_types
        )

    def setUp(self):
        """"Set up a test with database objects."""
        bill_id = self.creator.create_cost_entry_bill()
        cost_entry_id = self.creator.create_cost_entry(bill_id)
        product_id = self.creator.create_cost_entry_product()
        pricing_id = self.creator.create_cost_entry_pricing()
        reservation_id = self.creator.create_cost_entry_reservation()
        self.creator.create_cost_entry_line_item(
            bill_id,
            cost_entry_id,
            product_id,
            pricing_id,
            reservation_id
        )

    def tearDown(self):
        """Return the database to a pre-test state."""
        self.accessor._session.rollback()

        for table_name in REPORT_TABLES:
            tables = self.accessor._get_db_obj_query(table_name).all()
            for table in tables:
                self.accessor._session.delete(table)
        self.accessor.commit()

    def test_initializer(self):
        """Test initializer."""
        self.assertIsNotNone(self.report_schema)
        self.assertIsNotNone(self.accessor._session)
        self.assertIsNotNone(self.accessor._conn)
        self.assertIsNotNone(self.accessor._cursor)

    def test_get_psycopg2_connection(self):
        """Test the psycopg2 connection."""
        conn = self.accessor._get_psycopg2_connection()

        self.assertIsInstance(conn, psycopg2.extensions.connection)

    def test_get_psycopg2_cursor(self):
        """Test that a psycopg2 cursor is returned."""
        cursor = self.accessor._get_psycopg2_cursor()

        self.assertIsInstance(cursor, psycopg2.extensions.cursor)


    def test_close_psycopg2_connection_with_arg(self):
        """Test that the passed in psycopg2 connection is closed."""
        conn = self.accessor._get_psycopg2_connection()

        self.accessor.close_psycopg2_connection(conn)

        self.assertTrue(conn.closed)

    def test_close_psycopg2_connection_default(self):
        """Test that the accessor's psycopg2 connection is closed."""
        self.accessor.close_psycopg2_connection()

        self.assertTrue(self.accessor._conn.closed)
        # Return the accessor's connection to its open state
        self.accessor._conn = self.accessor._get_psycopg2_connection()

    def test_get_db_obj_query_default(self):
        """Test that a query is returned."""
        table_name = random.choice(REPORT_TABLES)

        query = self.accessor._get_db_obj_query(table_name)

        self.assertIsInstance(query, Query)

    def test_get_db_obj_query_with_columns(self):
        """Test that a query is returned with limited columns."""
        table_name = random.choice(REPORT_TABLES)
        columns = list(self.column_map[table_name].values())

        selected_columns = [random.choice(columns) for _ in range(2)]
        missing_columns = set(columns).difference(selected_columns)

        query = self.accessor._get_db_obj_query(
            table_name,
            columns=selected_columns
        )

        self.assertIsInstance(query, Query)

        result = query.first()

        for column in selected_columns:
            self.assertTrue(hasattr(result, column))

        for column in missing_columns:
            self.assertFalse(hasattr(result, column))

    def test_bulk_insert_rows(self):
        """Test that the bulk insert method inserts line items."""
        # Get data commited for foreign key relationships to work
        self.accessor.commit()

        table_name = LINE_ITEM_TABLE
        table = getattr(self.report_schema, table_name)
        column_map = self.column_map[table_name]
        query = self.accessor._get_db_obj_query(table_name)
        initial_count = query.count()
        cost_entry = query.first()

        data_dict = self.creator.create_columns_for_table(table_name)
        data_dict['cost_entry_bill_id'] = cost_entry.cost_entry_bill_id
        data_dict['cost_entry_id'] = cost_entry.cost_entry_id
        data_dict['cost_entry_product_id'] = cost_entry.cost_entry_product_id
        data_dict['cost_entry_pricing_id'] = cost_entry.cost_entry_pricing_id
        data_dict['cost_entry_reservation_id'] = cost_entry.cost_entry_reservation_id

        columns = list(data_dict.keys())
        values = list(data_dict.values())
        file_obj = self.creator.create_csv_file_stream(values)

        self.accessor.bulk_insert_rows(file_obj, table_name, columns)

        final_count = query.count()
        new_line_item = query.order_by(table.id.desc()).first()

        self.assertTrue(final_count > initial_count)

        for column in columns:
            value = getattr(new_line_item, column)
            if isinstance(value, datetime.datetime):
                value = self.creator.stringify_datetime(value)
            self.assertEqual(value, data_dict[column])

    def test_create_db_object(self):
        """Test that a mapped database object is returned."""
        table = random.choice(REPORT_TABLES)
        data = self.creator.create_columns_for_table(table)

        row = self.accessor.create_db_object(table, data)

        for column, value in data.items():
            self.assertEqual(getattr(row, column), value)

    def test_commit_db_object(self):
        """Test that a database object is committed to the database."""
        self.accessor._session.rollback()
        table = random.choice(REPORT_TABLES)
        data = self.creator.create_columns_for_table(table)

        row = self.accessor.create_db_object(table, data)

        query = self.accessor._get_db_obj_query(table)

        persisted_row = query.first()
        self.assertIsNone(persisted_row)

        self.accessor.commit_db_object(row)
        self.accessor._session.rollback()

        persisted_row = query.first()

        self.assertIsNotNone(persisted_row.id)

    def test_flush_db_object(self):
        """Test that the database flush moves the object to the database."""
        self.accessor._session.commit()
        table = random.choice(REPORT_TABLES)
        data = self.creator.create_columns_for_table(table)
        initial_row_count = self.accessor._get_db_obj_query(table).count()
        row = self.accessor.create_db_object(table, data)

        self.accessor.flush_db_object(row)
        self.assertIsNotNone(row.id)

        row_count = self.accessor._get_db_obj_query(table).count()
        self.assertTrue(row_count > initial_row_count)
        self.accessor._session.rollback()
        final_row_count = self.accessor._get_db_obj_query(table).count()
        self.assertEqual(initial_row_count, final_row_count)

    def test_clean_data(self):
        """Test that data cleaning produces proper data types."""
        table_name = random.choice(REPORT_TABLES)
        table = getattr(self.report_schema, table_name)
        column_types = self.report_schema.column_types[table_name]

        data = self.creator.create_columns_for_table(table_name)
        cleaned_data = self.accessor.clean_data(data, table_name)

        for key, value in cleaned_data.items():
            if column_types[key] == datetime.datetime:
                value = self.creator.datetimeify_string(value)
            self.assertIsInstance(value, column_types[key])

    def test_get_current_cost_entry_bill(self):
        """Test that the most recent cost entry bill is returned."""
        table_name = 'reporting_awscostentrybill'
        bill_id = self.accessor._get_db_obj_query(table_name).first().id
        bill = self.accessor.get_current_cost_entry_bill()

        self.assertEqual(bill_id, bill.id)

    def test_get_cost_entries(self):
        """Test that a dict of cost entries are returned."""
        table_name = 'reporting_awscostentry'
        query = self.accessor._get_db_obj_query(table_name)
        count = query.count()
        first_entry = query.first()
        cost_entries = self.accessor.get_cost_entries()

        self.assertIsInstance(cost_entries, dict)
        self.assertEqual(len(cost_entries.keys()), count)
        self.assertIn(first_entry.id, cost_entries.values())

    def test_get_products(self):
        """Test that a dict of products are returned."""
        table_name = 'reporting_awscostentryproduct'
        query = self.accessor._get_db_obj_query(table_name)
        count = query.count()
        first_entry = query.first()
        products = self.accessor.get_products()

        self.assertIsInstance(products, dict)
        self.assertEqual(len(products.keys()), count)
        self.assertIn(first_entry.sku, products)

    def test_get_pricing(self):
        """Test that a dict of pricing is returned."""
        table_name = 'reporting_awscostentrypricing'
        query = self.accessor._get_db_obj_query(table_name)
        count = query.count()
        first_entry = query.first()

        pricing = self.accessor.get_pricing()

        self.assertIsInstance(pricing, dict)
        self.assertEqual(len(pricing.keys()), count)
        self.assertIn(first_entry.id, pricing.values())

    def test_get_reservations(self):
        """Test that a dict of reservations are returned."""
        table_name = 'reporting_awscostentryreservation'
        query = self.accessor._get_db_obj_query(table_name)
        count = query.count()
        first_entry = query.first()

        reservations = self.accessor.get_reservations()

        self.assertIsInstance(reservations, dict)
        self.assertEqual(len(reservations.keys()), count)
        self.assertIn(first_entry.reservation_arn, reservations)
