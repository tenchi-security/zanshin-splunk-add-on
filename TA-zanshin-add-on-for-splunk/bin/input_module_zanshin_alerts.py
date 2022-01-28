
# encoding = utf-8

import os
import sys
import time
import json
from datetime import datetime

from zanshinsdk import Client
from zanshinsdk.alerts_history import AbstractPersistentAlertsIterator, PersistenceEntry

PORTAL_DOMAIN = "https://zanshin.tenchisecurity.com"


class HelperPersistentAlertsIterator(AbstractPersistentAlertsIterator):
    def __init__(self, helper, opt_name, *args, **kwargs):
        super(HelperPersistentAlertsIterator, self).__init__(*args, **kwargs)
        self._helper = helper
        self._opt_name = opt_name

    @property
    def helper(self):
        return self._helper

    @property
    def opt_name(self):
        return self._opt_name

    def _load(self):
        cursor = self.helper.get_check_point('%s:%s:%s:cursor' % (self.opt_name, self.organization_id, self.scan_target_ids))
        self.helper.log_info("checkpoint loaded: ")
        return PersistenceEntry(self.organization_id, self.scan_target_ids, cursor)

    def _save(self):
        self.helper.save_check_point('%s:%s:%s:cursor' % (self.opt_name, self.organization_id, self.scan_target_ids), self.persistence_entry.cursor)
        self.helper.log_info("checkpoint saved: ")

    def __str__(self):
        return super(HelperPersistentAlertsIterator, self).__str__()[:-1]


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # api_key = definition.parameters.get('api_key', None)
    # organization_id = definition.parameters.get('organization_id', None)
    pass

def collect_events(helper, ew):
    helper.log_info("Collect_events Zanshin Alerts start!!!")

    opt_name = helper.get_arg("name")
    opt_api_key = helper.get_arg("api_key")
    opt_organization_id = helper.get_arg("organization_id")
    opt_scan_target_ids = helper.get_arg("scan_target_ids")

    if not opt_api_key:
        raise ValueError("")

    if not opt_organization_id:
        raise ValueError("")

    if not opt_scan_target_ids:
        opt_scan_target_ids = []
    else:
        opt_scan_target_ids = [x.strip() for x in opt_scan_target_ids.split(',')]

    _client = Client(api_key=opt_api_key)

    organization = _client.get_organization(opt_organization_id)
    scanTargets = _client.iter_organization_scan_targets(opt_organization_id)

    iter_alerts = HelperPersistentAlertsIterator(helper, opt_name, opt_organization_id, opt_scan_target_ids)

    for alert in iter_alerts:
        try:
            scanTargetName = 'undefined'
            for scanTarget in scanTargets:
                if scanTarget['id'] == alert['scanTargetId']:
                    scanTargetName = scanTarget['name']
                    break

            _alert = {
                "alert_id": alert['id'],
                "alert_version": alert['version'],
                "organization_id": alert['organizationId'],
                "organization_name": organization['name'],
                "scan_target_id": alert['scanTargetId'],
                "scan_target_name": scanTargetName,
                "resource": alert['resource'],
                "rule": alert['rule'],
                "severity": alert['severity'],
                "tags": alert['tags'],
                "compliances": alert['compliances'],
                "labels": alert['labels'],
                "metadata": alert['metadata'],
                "enrichment": alert['enrichment'],
                "state": alert['state'],
                "date": alert['date'],
                "alert_pure": alert['rulePure'],
                "permalink": f"{PORTAL_DOMAIN}/alert/{alert['id']}",
            }

            utc_dt = datetime.strptime(alert['date'], '%Y-%m-%dT%H:%M:%S.%fZ')

            event = helper.new_event(time=(utc_dt - datetime(1970, 1, 1)).total_seconds(),
                                     source=helper.get_input_type(),
                                     index=helper.get_output_index(),
                                     sourcetype=helper.get_sourcetype(),
                                     data=json.dumps(_alert))

            ew.write_event(event)
            helper.log_info(f"Wrote alert {alert['id']}")
            helper.log_info('saving check point')
            iter_alerts.save()
        except Exception as e:
            helper.log_error(f"Error writing alert {alert['id']}")
            raise e
    helper.log_info(f"[{opt_name}]Collect events finished for organization {organization['id']}")

