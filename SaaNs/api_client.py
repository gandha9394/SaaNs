import requests
import logging
import json
from requests import Response
from .schema import PushRequestBody, ReportRequestBody
import httpx
import asyncio


# curl -H 'Content-Type: application/json'
# -d '{"metric":"x.y.z","value":600.34,"tags":{"t1":"v1","t2":"v2"}}'
# VM_ENDPOINT= "http://localhost:4242/api/put"
VM_SELECT_ENDPOINT = "https://saans.dev.sahamati.org.in/select/0/prometheus/api/v1/query"
VM_INSERT_ENDPOINT = "https://saans.dev.sahamati.org.in/insert/0/prometheus/"

# VM_SELECT_ENDPOINT = "https://saans.free.beeceptor.com"
# VM_INSERT_ENDPOINT = "https://saans.free.beeceptor.com"

def push(data: PushRequestBody) -> Response:
    # TODO add exponential backoff
    try:
        logging.info("--------------------")
        logging.info(data)
        response = requests.post(
            url=VM_INSERT_ENDPOINT+"api/v1/import",
            data=data, verify=False,
            headers={"Content-Type": "application/json"},
        )
        logging.info("Pushed metric")
        logging.info(response.content)
        logging.info(response.status_code)
        return response
    except Exception as e:
        logging.error("Failed to push metric!")
        logging.exception(e)

async def call_url(session, url):
    response = await session.request(method='GET',url=VM_SELECT_ENDPOINT+url)
    return response

async def fetch(data) -> str:
    # TODO add exponential backoff
    try:
        loop = asyncio.get_event_loop()
        logging.info("--------------------")
        logging.info(data)
        async with httpx.AsyncClient() as session:  #use httpx
             responses = await asyncio.gather(*[call_url(session, x) for x in data])
        session.aclose()
        
        logging.info("fetched metric")
        for response in responses:
            logging.info(response.content)
            logging.info(response.status_code)
        return responses
    except Exception as e:
        logging.error("Failed to push metric!")
        logging.exception(e)


