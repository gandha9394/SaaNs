import requests
import logging
import json
from .schema import MetricType
# curl -H 'Content-Type: application/json' 
# -d '{"metric":"x.y.z","value":600.34,"tags":{"t1":"v1","t2":"v2"}}'
VM_ENDPOINT= "http://localhost:4242/api/put"

def push(data: MetricType)-> str:
    # TODO add exponential backoff
    try:

        response = requests.post(url=VM_ENDPOINT, data=json.dumps(data))
        logging.info('Pushed metric')
        logging.info(response)
    except Exception as e:
        logging.error("Failed to push metric!")
        logging.exception(e)

