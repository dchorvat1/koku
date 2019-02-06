# Generated by Django 2.1.5 on 2019-02-05 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0026_auto_20190130_1746'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DROP VIEW IF EXISTS reporting_ocpawscostlineitem_daily;

            CREATE OR REPLACE VIEW reporting_ocpawscostlineitem_daily AS (
                SELECT ocp.cluster_id,
                    ocp.cluster_alias,
                    ocp.namespace,
                    ocp.pod,
                    ocp.node,
                    ocp.pod_labels,
                    ocp.pod_usage_cpu_core_seconds,
                    ocp.pod_request_cpu_core_seconds,
                    ocp.pod_limit_cpu_core_seconds,
                    ocp.pod_usage_memory_byte_seconds,
                    ocp.pod_request_memory_byte_seconds,
                    ocp.node_capacity_cpu_cores,
                    ocp.node_capacity_cpu_core_seconds,
                    ocp.node_capacity_memory_bytes,
                    ocp.node_capacity_memory_byte_seconds,
                    ocp.cluster_capacity_cpu_core_seconds,
                    ocp.cluster_capacity_memory_byte_seconds,
                    aws.cost_entry_product_id,
                    aws.cost_entry_pricing_id,
                    aws.cost_entry_reservation_id,
                    aws.line_item_type,
                    aws.usage_account_id,
                    aws.usage_start,
                    aws.usage_end,
                    aws.product_code,
                    aws.usage_type,
                    aws.operation,
                    aws.availability_zone,
                    aws.resource_id,
                    aws.usage_amount,
                    aws.normalization_factor,
                    aws.normalized_usage_amount,
                    aws.currency_code,
                    aws.unblended_rate,
                    aws.unblended_cost,
                    aws.blended_rate,
                    aws.blended_cost,
                    aws.public_on_demand_cost,
                    aws.public_on_demand_rate,
                    aws.tax_type,
                    aws.tags
                FROM reporting_awscostentrylineitem_daily as aws
                JOIN reporting_ocpusagelineitem_daily as ocp
                    ON aws.resource_id = ocp.resource_id
                        AND aws.usage_start::date = ocp.usage_start::date
            );
            """
        )
    ]
