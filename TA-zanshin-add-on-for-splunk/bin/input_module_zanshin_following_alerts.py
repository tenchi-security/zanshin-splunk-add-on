
# encoding = utf-8

import os
import sys
import time
import json
from datetime import datetime, timedelta

from zanshinsdk import Client

PORTAL_DOMAIN = "https://zanshin.tenchisecurity.com"

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

    following = _client.iter_organization_following(opt_organization_id)
    
    start_date = None
    
    helper.log_info("get check point")
    latest_date = helper.get_check_point('%s:%s:following:last_date' % (opt_name, opt_organization_id))
    
    if latest_date:
        start_date = latest_date


    for alert in _client.iter_following_alerts(opt_organization_id, opt_following_ids, start_date=start_date, historical=True):
        try:
            followingName = 'undefined'
            for f in following:
                if f['id'] == alert['followingId']:
                    followingName = f['name']
                    break

            _alert = {
                "alert_id": alert['id'],
                "alert_version": alert['version'],
                "following_name": followingName,
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
                "following_id": alert['followingId'],
                "permalink": f"{PORTAL_DOMAIN}/alert/{alert['id']}",
            }

            utc_dt = datetime.strptime(alert['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            utc_dt = utc_dt + timedelta(milliseconds=1)

            event = helper.new_event(time=(utc_dt - datetime(1970, 1, 1)).total_seconds(),
                                    source=helper.get_input_type(),
                                    index=helper.get_output_index(),
                                    sourcetype=helper.get_sourcetype(),
                                    data=json.dumps(_alert))

            ew.write_event(event)
            helper.log_info(f"Wrote alert {alert['id']}")

            current_date = helper.get_check_point('%s:%s:following:last_date' % (opt_name, opt_organization_id))

            if current_date:
                cp_utc_dt = datetime.strptime(current_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                if (utc_dt >= cp_utc_dt):
                    helper.save_check_point('%s:%s:following:last_date' % (opt_name, opt_organization_id), utc_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
                    helper.log_info("saving check point")
            else:
                helper.save_check_point('%s:%s:following:last_date' % (opt_name, opt_organization_id), utc_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
                helper.log_info("saving check point")

        except Exception as e:
            helper.log_error(f"Error writing alert {alert['id']}")
            raise e
    helper.log_info(f"Collect events finished for organization {opt_organization_id}")
