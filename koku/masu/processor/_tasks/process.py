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
"""Asynchronous tasks."""

from os import path

import psutil
from celery.utils.log import get_task_logger

from masu.database.provider_db_accessor import ProviderDBAccessor
from masu.database.report_manifest_db_accessor import ReportManifestDBAccessor
from masu.database.report_stats_db_accessor import ReportStatsDBAccessor
from masu.processor.report_processor import ReportProcessor

LOG = get_task_logger(__name__)


# pylint: disable=too-many-arguments,too-many-locals
def _process_report_file(schema_name, provider, provider_uuid, report_dict):
    """
    Task to process a Report.

    Args:
        schema_name   (String) db schema name
        provider      (String) provider type
        provider_uuid (String) provider uuid
        report_dict   (dict) The report data dict from previous task

    Returns:
        None

    """
    start_date = report_dict.get('start_date')
    report_path = report_dict.get('file')
    compression = report_dict.get('compression')
    manifest_id = report_dict.get('manifest_id')
    provider_id = report_dict.get('provider_id')
    stmt = ('Processing Report:'
            ' schema_name: {},'
            ' report_path: {},'
            ' compression: {},'
            ' provider: {},'
            ' start_date: {}')
    log_statement = stmt.format(schema_name,
                                report_path,
                                compression,
                                provider,
                                start_date)
    print(log_statement)
    mem = psutil.virtual_memory()
    mem_msg = 'Avaiable memory: {} bytes ({}%)'.format(mem.free, mem.percent)
    print(mem_msg)

    file_name = report_path.split('/')[-1]
    print('IN _PROCESS_REPORT_FILE')
    with ReportStatsDBAccessor(file_name, manifest_id) as stats_recorder:
        stats_recorder.log_last_started_datetime()
        stats_recorder.commit()
        print("CALLING OCP PROCESSOR")
        processor = ReportProcessor(schema_name=schema_name,
                                    report_path=report_path,
                                    compression=compression,
                                    provider=provider,
                                    provider_id=provider_id,
                                    manifest_id=manifest_id)
        print('CALLING processor.process()')
        processor.process()
        stats_recorder.log_last_completed_datetime()
        stats_recorder.commit()

    with ReportManifestDBAccessor() as manifest_accesor:
        manifest = manifest_accesor.get_manifest_by_id(manifest_id)
        if manifest:
            manifest.num_processed_files += 1
            manifest_accesor.mark_manifest_as_updated(manifest)
            manifest_accesor.commit()
        else:
            print('Unable to find manifest for ID: %s, file %s', manifest_id, file_name)

    with ProviderDBAccessor(provider_uuid=provider_uuid) as provider_accessor:
        provider_accessor.setup_complete()
        provider_accessor.commit()

    files = processor.remove_processed_files(path.dirname(report_path))
    print('Temporary files removed: %s', str(files))