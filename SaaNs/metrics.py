import logging
import json
from requests import RequestException
from .schema import PushRequestBody
from .api_client import push, fetch
from datetime import datetime, timedelta


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
                logging.info(f'-------{event.name}')
                metric = f"{event.name}.{j}"
                logging.info(json_event)
                if j != "name" and j !='fipId':
                    response = push(
                        json.dumps(
                            {
                                "metric": {"__name__": metric, "fipId": event.fipId},
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
        query += f'{{fipId=\'{fip_str}\'}}'
    if delta:
        query+=f'[{delta}]'
    if time:
        query+= f' @ {time}'
    query +=') keep_metric_names'
    logging.info(f'QUERY={query}')
    return query

async def get_report(query):
    duration = query.duration
    evaluate_at = datetime.strptime(
        query.evaluate_at, "%Y-%m-%dT%H:%M:%S.%fZ"
    ) + timedelta(hours=5, minutes=30)
    evaluate_at = evaluate_at.timestamp()

    resp = await fetch(
            # "?query=avg_over_time(FIP_ACCOUNT_DISCOVERY.latencyP95_ms[12h])",
            # "?query=avg_over_time(FIP_ACCOUNT_DISCOVERY.latency_ms[12h])",
        [
            get_promql_query("avg_over_time","FIP_ACCOUNT_DISCOVERY.latencyP90_ms",evaluate_at,duration, query.fipIds),
            get_promql_query('avg_over_time','FIP_ACCOUNT_DISCOVERY.latencyP95_ms',evaluate_at,duration,query.fipIds),
            get_promql_query('avg_over_time','FIP_ACCOUNT_DISCOVERY.latencyP50_ms',evaluate_at,duration,query.fipIds),
            get_promql_query("avg_over_time","FIP_ACCOUNT_DISCOVERY.latency_ms",evaluate_at,duration,query.fipIds),
            get_promql_query("sum_over_time","FIP_ACCOUNT_DISCOVERY.total_count",evaluate_at,duration,query.fipIds),
            get_promql_query("sum_over_time","FIP_ACCOUNT_DISCOVERY.failure_count",evaluate_at,duration,query.fipIds),
            get_promql_query("sum_over_time","FIP_ACCOUNT_DISCOVERY.success_count",evaluate_at,duration,query.fipIds),
        ]
    )
    metric_responses = {
        "latencyP90_ms": "",
        "latencyP95_ms": "",
        "latencyP50_ms": "",
        "latency_ms": "",
        "total_count": "",
        "failure_count": "",
        "success_count": "",
    }
    i = 0
    for m_r in metric_responses:
        j_resp = json.loads(resp[i].content)
        if j_resp['status'] == 'success':
            if len(j_resp.get("data").get("result")):
                metric = j_resp["data"]["result"][0]
                metric_responses[m_r] = metric["value"][1]
            else:
                metric_responses[m_r] = None
            i += 1
        else:
            logging.error(f'Failed to fetch for metric - {m_r}')
            metric_responses[m_r] = None
    logging.info("all data?")
    logging.info(metric_responses)
    event = {
        "event": "FIP_ACCOUNT_DISCOVERY",
    }
    return dict(list(event.items()) + list(metric_responses.items()))
