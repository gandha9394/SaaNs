import logging
import json
from .schema import PushRequestBody, ReportRequestBody
from .metrics import account_discovery_metric, get_report
from requests import RequestException
import azure.functions
import asyncio

async def get_report_async(report_query):
    res = await get_report(report_query)
    logging.info('-----------------------')
    logging.info(json.dumps(res))
    return json.dumps(res)

def format_error(code, message):
    return json.dumps({"success":False,"code":code,"message":message})

def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    report = req.params.get('report')
    logging.info(req.url)
    if req.method == 'POST':
        if not report:
            try:
                req_body = req.get_json()
                body = PushRequestBody(**req_body)
            except ValueError as e:
                logging.error('Value error')
                return azure.functions.HttpResponse(format_error("validation_error",str(e)), headers={'content-type':'application/json'})
            try:
                account_discovery_metric(body)
                return azure.functions.HttpResponse('{"success":true,"message":"Successfully pushed metric"}',headers={'content-type':'application/json'}, status_code = 200)
            except RequestException as e:
                return azure.functions.HttpResponse(format_error("api_error",str(e)), headers={'content-type':'application/json'}, status_code=400)
        if report:
            try:
                req_body = req.get_json()
                report_query = ReportRequestBody(**req_body)
                report_response = asyncio.run(get_report_async(report_query))
                return azure.functions.HttpResponse(report_response,headers={'content-type':'application/json'})
            except ValueError as e:
                return azure.functions.HttpResponse(format_error("validation_error",str(e)), headers={'content-type':'application/json'}, status_code=400)
    else:
        return azure.functions.HttpResponse(
            "Invalid operation. Please use POST method on /api/push or /api/push APIs.",
            status_code=400
        )
