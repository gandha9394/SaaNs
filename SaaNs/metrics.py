import logging
from .api_client import push
from datetime import datetime
def account_discovery_metric(json_payload):
    
    event = 'ACCOUNT_DISCOVERY'
    time = datetime.strptime(json_payload['end_time'], "%Y-%m-%dT%H:%M:%S.%fZ") # handle different time stamps
    metric_obj = []
    fips = json_payload['fips']
    for fip in fips:
        for i in range(len(fips[fip])):
            for j in fips[fip][i]:
                if j != 'event':
                    metric = f"{fips[fip][i]['event']}.{j}"
                    metric_obj.append( {
                        'metric': metric,
                        'timestamp': time.timestamp(),
                        'value':fips[fip][i][j],
                        'tags':{
                            'fipId': fip 
                        }
                    })
    if len(metric_obj) > 0:
        logging.info(metric_obj)
        push(metric_obj)