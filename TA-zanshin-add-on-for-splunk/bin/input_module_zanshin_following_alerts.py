
# encoding = utf-8

import os
import sys
import time
import json
from datetime import datetime

from zanshinsdk import Client
from zanshinsdk.iterator import AbstractPersistentAlertsIterator, PersistenceEntry

PORTAL_DOMAIN = "https://zanshin.tenchisecurity.com"


class HelperPersistentFollowingAlertsIterator(AbstractPersistentAlertsIterator):
    def __init__(self, helper, opt_name, following_ids, *args, **kwargs):
        super(HelperPersistentFollowingAlertsIterator, self).__init__(field_name='following_ids',
                                                                      filter_ids=following_ids, *args, **kwargs)
        self._helper = helper
        self._opt_name = opt_name

    @property
    def helper(self):
        return self._helper

    @property
    def opt_name(self):
        return self._opt_name

    def _load_alerts(self):
        return self.client.iter_alerts_following_history(
            organization_id=self.persistence_entry.organization_id,
            following_ids=self.persistence_entry.filter_ids,
            cursor=self.persistence_entry.cursor
        )

    def _load(self):
        cursor = self.helper.get_check_point('%s:%s:%s:cursor' % (self.opt_name, self._organization_id, self._filter_ids))
        self.helper.log_info(f"checkpoint loaded: {cursor}")
        return PersistenceEntry(self._organization_id, self._filter_ids, cursor)

    def _save(self):
        self.helper.save_check_point('%s:%s:%s:cursor' % (self.opt_name, self._organization_id, self._filter_ids),
                                     self.persistence_entry.cursor)
        self.helper.log_info(f"checkpoint saved: {self.persistence_entry.cursor}")


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # api_key = definition.parameters.get('api_key', None)
    # organization_id = definition.parameters.get('organization_id', None)
    pass

def collect_events(helper, ew):
    helper.log_info("Collect_events Zanshin Following Alerts start!!!")

    opt_name = helper.get_arg("name")
    opt_api_key = helper.get_arg("api_key")
    opt_organization_id = helper.get_arg("organization_id")
    opt_following_ids = helper.get_arg("following_ids")

    if not opt_api_key:
        raise ValueError("")

    if not opt_organization_id:
        raise ValueError("")

    if not opt_following_ids:
        opt_following_ids = []
    else:
        opt_following_ids = [x.strip() for x in opt_following_ids.split(',')]

    _client = Client(api_key=opt_api_key)

    _following = _client.iter_organization_following(opt_organization_id)

    following = list(_following)

    iter_alerts = HelperPersistentFollowingAlertsIterator(helper, opt_name, client=_client,
                                                          organization_id=opt_organization_id,
                                                          following_ids=opt_following_ids)

    for alert in iter_alerts:
        try:
            following_name = 'undefined'
            for f in following:
                if f['id'] == alert['followingId']:
                    following_name = f['name']
                    break

            _alert = {
                "alert_id": alert['id'],
                "alert_version": alert['version'],
                "following_id": alert['followingId'],
                "following_name": following_name,
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
            helper.log_info(f"Wrote alert {alert['id']} version {alert['version']}")
            helper.log_info('saving check point')
            iter_alerts.save()
        except Exception as e:
            helper.log_error(f"Error writing alert {alert['id']} version {alert['version']}")
            raise e
    helper.log_info(f"Collect events finished for {opt_name} input")
