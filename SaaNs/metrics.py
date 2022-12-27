import logging
import json
from requests import RequestException
from .schema import PushRequestBody, ReportRequestBody
from .api_client import push, fetch, fetch_bulk
from datetime import datetime, timedelta
from copy import deepcopy


def account_discovery_metric(body: PushRequestBody):

    time = datetime.strptime(
        body.end_time, "%Y-%m-%dT%H:%M:%S.%fZ"
    ) + timedelta(hours=5, minutes=30)
    # handle different time stamps
    events = body.events
    try:
        for event in events:
            logging.info(event)
            json_event = event.dict()
            for j in json_event:
                metric = f"{event.name}.{j}"
                logging.info(json_event)
                if j != "name" and j !='fipId':
                    response = push(
                        json.dumps(
                            {
                                "metric": {"__name__": metric, "type":j, "fipId": event.fipId},
                                "timestamps": [int(time.timestamp() * 1000)],
                                "values": [json_event[j]],
                            }
                        )
                    )
                    if response.status_code > 204:
                        logging.error(response.content)
                        raise RequestException("VM insert failed.")

    except (RequestException) as e:
        logging.error(e)
        raise RequestException("Something went wrong")


# {"metric":{"__name__":"bloo","fipId":"ICICI"},"values":[32],"timestamps":[1671080782438]}


def get_promql_query(type,metric, time=None, delta=None, fip=None):
    query = f"?query={type}({metric}"
    if fip:
        fip_str = '|'.join(fip)
        query += f'{{fipId=~\'{fip_str}\'}}'
    if delta:
        query+=f'[{delta}]'
    if time:
        query+= f' @ {time}'
    query +=') keep_metric_names'
    logging.info(f'QUERY={query}')
    return query

async def get_metric_count(time,delta, fip):
    response = await fetch(get_promql_query('count_over_time','FIP_ACCOUNT_DISCOVERY.total_count',time, delta, fip))
    logging.info('----------')
    logging.info(response.content)
    body = json.loads(response.content)
    if body['status'] == 'success':
        total = 0
        data = body['data']
        for i in data['result']:
            total += int(i['value'][1])
        return total

async def get_report(query: ReportRequestBody):
    duration = query.duration
    evaluate_at = datetime.strptime(
        query.evaluate_at, "%Y-%m-%dT%H:%M:%S.%fZ"
    ) + timedelta(hours=5, minutes=30)
    evaluate_at = evaluate_at.timestamp()
    resp = []
    for e_names in query.events:
       resp += await fetch_bulk(
                # "?query=avg_over_time(FIP_ACCOUNT_DISCOVERY.latencyP95_ms[12h])",
                # "?query=avg_over_time(FIP_ACCOUNT_DISCOVERY.latency_ms[12h])",
            [
                get_promql_query("avg_over_time",f"{e_names}.latencyP90_ms",evaluate_at,duration, query.fipIds),
                get_promql_query('avg_over_time',f'{e_names}.latencyP95_ms',evaluate_at,duration,query.fipIds),
                get_promql_query('avg_over_time',f'{e_names}.latencyP50_ms',evaluate_at,duration,query.fipIds),
                get_promql_query("avg_over_time",f"{e_names}.latency_ms",evaluate_at,duration,query.fipIds),
                get_promql_query("sum_over_time",f"{e_names}.total_count",evaluate_at,duration,query.fipIds),
                get_promql_query("sum_over_time",f"{e_names}.failure_count",evaluate_at,duration,query.fipIds),
                get_promql_query("sum_over_time",f"{e_names}.success_count",evaluate_at,duration,query.fipIds),
            ]
        )
    event_template = {
            "latencyP90_ms": None,
            "latencyP95_ms": None,
            "latencyP50_ms": None,
            "latency_ms": None,
            "total_count": None,
            "failure_count": None,
            "success_count": None,
        }

    fip_responses = {}

    for events in resp:
        # logging.info(events.content)
        events_json = json.loads(events.content)
        if events_json['status'] == 'success':
            if len(events_json.get("data").get("result")):
                for event_metric in events_json["data"]["result"]:
                    event_name = event_metric['metric']['__name__']
                    main_event= event_name.split('.')[0]
                    sub_event = event_name.split('.')[-1]
                    fip_name = event_metric['metric']['fipId']
                    if sub_event == main_event:
                        raise Exception()
                    logging.info(f'{fip_name} - {main_event} - {sub_event} - { event_metric["value"][1]}')
                    if not fip_responses.get(fip_name):
                        fip_responses[fip_name]={
                            main_event: deepcopy(event_template)
                        }
                    if not fip_responses[fip_name].get(main_event):
                        fip_responses[fip_name][main_event] = deepcopy(event_template)
                        
                   
                    fip_responses[fip_name][main_event][sub_event] = event_metric["value"][1]
            else:
                logging.error('I have something which I cant fit here')
        logging.info(fip_responses)
    logging.info("all data?")
    count = await get_metric_count(evaluate_at, duration, query.fipIds)
    events_output = {
        "meta_data":{
            "event_count": count
        },
        'events':[]
    }
    logging.info(f'events{events_output}')
    for i in query.fipIds:
        if not fip_responses.get(i):
            empty_event = deepcopy(event_template)
            empty_event['fipId']=i
            empty_event['event']=None
            events_output['events'].append(empty_event)
            continue
        # logging.info(events["events"])
        for j in query.events:
            if not fip_responses[i].get(j):
                empty_event = deepcopy(event_template)
                empty_event['fipId']=i
                empty_event['event']=j
                events_output['events'].append(empty_event)
                continue
            logging.info(fip_responses[i])
            fip_event = fip_responses[i][j]
            fip_event['fipId']= i
            fip_event['event']=j
            events_output['events'].append(fip_event)
    return events_output

# FIP_ACCOUNT_DISCOVERY{type=~"latencyP50_ms",fipId=~"AGYA"}