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
"""Provider Mapper for Azure Reports."""

from django.db.models import CharField, DecimalField, Max, Sum, Value
from django.db.models.functions import Coalesce

from api.report.provider_map import ProviderMap
from reporting.models import AzureCostEntryLineItemDailySummary


class AzureProviderMap(ProviderMap):
    """Azure Provider Map."""

    def __init__(self, provider, report_type):
        """Constructor."""
        self._mapping = [
            {
                'provider': 'AZURE',
                'alias': '',
                'annotations': {
                    'subscription': 'cost_entry_bill__subscription_guid',
                    'service': 'service__service_name',
                    'resource_location': 'cost_entry_product__resource_location'
                },
                'end_date': 'usage_datetime',
                'filters': {
                    'subscription': [
                        {
                            'field': 'cost_entry_bill__subscription_guid',
                            'operation': 'icontains',
                            'composition_key': 'account_filter'
                        },
                    ],
                    'service': {
                        'field': 'service__service_name',
                        'operation': 'icontains'
                    },
                    'resource_location': {
                        'field': 'cost_entry_product__resource_location',
                        'operation': 'icontains'
                    },
                    'resource_type': {
                        'field': 'cost_entry_product__resource_type',
                        'operation': 'icontains'
                    }
                },
                'group_by_options': ['service', 'subscription',
                                     'resource_location', 'resource_type'],
                'tag_column': 'tags',
                'report_type': {
                    'costs': {
                        'aggregates': {
                            'infrastructure_cost': Sum('pretax_cost'),
                            'derived_cost': Sum(Value(0, output_field=DecimalField())),
                            'cost': Sum('pretax_cost')
                        },
                        'aggregate_key': 'pretax_cost',
                        'annotations': {
                            'infrastructure_cost': Sum('pretax_cost'),
                            'derived_cost': Value(0, output_field=DecimalField()),
                            'cost': Sum('pretax_cost'),
                            'cost_units': Coalesce(Max('meter__currency'), Value('USD'))
                        },
                        'delta_key': {'cost': Sum('pretax_cost')},
                        'filter': {},
                        'cost_units_key': 'meter__currency',
                        'cost_units_fallback': 'USD',
                        'sum_columns': ['cost', 'infrastructure_cost', 'derived_cost'],
                        'default_ordering': {'cost': 'desc'},
                    },
                    'instance_type': {
                        'aggregates': {
                            'infrastructure_cost': Sum('pretax_cost'),
                            'derived_cost': Sum(Value(0, output_field=DecimalField())),
                            'cost': Sum('pretax_cost'),
                            'count': Sum(Value(0, output_field=DecimalField())),
                            'usage': Sum('usage_quantity'),
                        },
                        'aggregate_key': 'usage_quantity',
                        'annotations': {
                            'infrastructure_cost': Sum('pretax_cost'),
                            'derived_cost': Value(0, output_field=DecimalField()),
                            'cost': Sum('pretax_cost'),
                            'cost_units': 'meter__currency',
                            'count': Sum('usage_quantity'),
                            'count_units': Value('instances', output_field=CharField()),
                            'usage': Sum('usage_quantity'),
                            'usage_units': 'Hrs'
                        },
                        'delta_key': {'usage': Sum('usage_quantity')},
                        'filter': {
                            'field': 'meter__meter_name',
                            'operation': 'isnull',
                            'parameter': False
                        },
                        'group_by': ['meter__meter_name'],
                        'cost_units_key': 'meter__currency',
                        'cost_units_fallback': 'USD',
                        'usage_units_key': '',
                        'usage_units_fallback': 'Hrs',
                        'count_units_fallback': 'things',
                        'sum_columns': ['usage', 'cost', 'infrastructure_cost',
                                        'derived_cost', 'count'],
                        'default_ordering': {'usage': 'desc'},
                    },
                    'storage': {
                        'aggregates': {
                            'usage': Sum('usage_quantity'),
                            'infrastructure_cost': Sum('pretax_cost'),
                            'derived_cost': Sum(Value(0, output_field=DecimalField())),
                            'cost': Sum('pretax_cost')
                        },
                        'aggregate_key': 'usage_quantity',
                        'annotations': {
                            'infrastructure_cost': Sum('pretax_cost'),
                            'derived_cost': Value(0, output_field=DecimalField()),
                            'cost': Sum('pretax_cost'),
                            'cost_units': Coalesce(Max('meter__currency'), Value('USD')),
                            'usage': Sum('usage_quantity'),
                            'usage_units': Coalesce(Max('unit'), Value('GB-Mo'))
                        },
                        'delta_key': {'usage': Sum('usage_quantity')},
                        'filter': {
                            'field': 'product_family',
                            'operation': 'contains',
                            'parameter': 'Storage'
                        },
                        'cost_units_key': 'meter__currency',
                        'cost_units_fallback': 'USD',
                        'usage_units_key': '',
                        'usage_units_fallback': 'GB-Mo',
                        'sum_columns': ['usage', 'cost', 'infrastructure_cost', 'derived_cost'],
                        'default_ordering': {'usage': 'desc'},
                    },
                },
                'start_date': 'usage_start',
                'tables': {
                    'query': AzureCostEntryLineItemDailySummary,
                },
            },
        ]
        super().__init__(provider, report_type)
