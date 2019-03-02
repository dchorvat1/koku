# Generated by Django 2.1.5 on 2019-03-01 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0040_auto_20190226_1538'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DROP VIEW IF EXISTS reporting_ocpawsstoragelineitem_daily;

            CREATE OR REPLACE VIEW reporting_ocpawsstoragelineitem_daily AS (
                WITH cte_storage_tag_matchted as (
                    SELECT aws.id as aws_id,
                            COALESCE(pvl.id, pvcl.id) as ocp_id,
                            aws.usage_start,
                            COALESCE(pvl.namespace, pvcl.namespace) as namespace
                        FROM (
                        SELECT aws.id,
                            aws.usage_start,
                            LOWER(key) as key,
                            LOWER(value) as value
                            FROM reporting_awscostentrylineitem_daily as aws,
                                jsonb_each_text(aws.tags) labels
                        ) AS aws
                        LEFT JOIN (
                            SELECT ocp.id,
                                ocp.usage_start,
                                ocp.cluster_alias,
                                ocp.node,
                                ocp.namespace,
                                LOWER(key) as key,
                                LOWER(value) as value
                            FROM reporting_ocpstoragelineitem_daily as ocp,
                                jsonb_each_text(ocp.persistentvolume_labels) labels
                        ) AS pvl
                            ON aws.usage_start::date = pvl.usage_start::date
                                AND (
                                    (aws.key = pvl.key AND aws.value = pvl.value)
                                    OR (aws.key = 'openshift_cluster' AND aws.value = pvl.cluster_alias)
                                    OR (aws.key = 'openshift_node' AND aws.value = pvl.node)
                                    OR (aws.key = 'openshift_project' AND aws.value = pvl.namespace)
                                )
                        LEFT JOIN (
                            SELECT ocp.id,
                                ocp.usage_start,
                                ocp.cluster_alias,
                                ocp.node,
                                ocp.namespace,
                                LOWER(key) as key,
                                LOWER(value) as value
                            FROM reporting_ocpstoragelineitem_daily as ocp,
                                jsonb_each_text(ocp.persistentvolumeclaim_labels) labels
                    ) AS pvcl
                            ON aws.usage_start::date = pvcl.usage_start::date
                                AND (
                                    (aws.key = pvcl.key AND aws.value = pvcl.value)
                                    OR (aws.key = 'openshift_cluster' AND aws.value = pvcl.cluster_alias)
                                    OR (aws.key = 'openshift_node' AND aws.value = pvcl.node)
                                    OR (aws.key = 'openshift_project' AND aws.value = pvcl.namespace)
                                )
                    WHERE (pvl.id IS NOT NULL OR pvcl.id IS NOT NULL) OR pvl.id = pvcl.id
                    GROUP BY aws.usage_start, aws.id, pvl.id, pvcl.id, pvl.namespace, pvcl.namespace
                ),
                cte_number_of_shared_projects AS (
                    SELECT usage_start,
                        aws_id,
                        count(DISTINCT namespace) as shared_projects
                    FROM cte_storage_tag_matchted
                    GROUP BY usage_start, aws_id
                )
                SELECT ocp.cluster_id,
                    ocp.cluster_alias,
                    ocp.namespace,
                    ocp.pod,
                    ocp.node,
                    ocp.persistentvolumeclaim,
                    ocp.persistentvolume,
                    ocp.storageclass,
                    ocp.persistentvolumeclaim_capacity_bytes,
                    ocp.persistentvolumeclaim_capacity_byte_seconds,
                    ocp.volume_request_storage_byte_seconds,
                    ocp.persistentvolumeclaim_usage_byte_seconds,
                    ocp.persistentvolume_labels,
                    ocp.persistentvolumeclaim_labels,
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
                    aws.tags,
                    tm.shared_projects
                FROM (
                    SELECT tm.usage_start,
                        tm.ocp_id,
                        tm.aws_id,
                        max(sp.shared_projects) as shared_projects
                    FROM cte_storage_tag_matchted AS tm
                    LEFT JOIN cte_number_of_shared_projects AS sp
                        ON tm.aws_id = sp.aws_id
                    GROUP BY tm.usage_start, tm.ocp_id, tm.aws_id
                ) AS tm
                JOIN reporting_awscostentrylineitem_daily as aws
                    ON tm.aws_id = aws.id
                JOIN reporting_ocpstoragelineitem_daily as ocp
                    ON tm.ocp_id = ocp.id
            )
            ;
            """
        )
    ]
