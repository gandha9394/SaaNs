import logging
import json
from .schema import PushRequestBody, ReportRequestBody
from .metrics import account_discovery_metric, get_report
from requests import RequestException
import azure.functions
import asyncio
from .utils import verify_and_decode_credentials

async def get_report_async(report_query):
    res = await get_report(report_query)
    return json.dumps(res)

def format_error(code, message):
    return json.dumps({"success":False,"code":code,"message":message})

def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    api_type = req.route_params.get('type')
    logging.info(req.route_params.get('type'))
    logging.info(req.url)
    if req.method == 'POST':
        if api_type == 'push':
            
            try:
                auth = req.headers.get('x-api-key','')
                logging.info(auth)
                claim = verify_and_decode_credentials(auth, 'AA')
                aaId= claim['azp']
                req_body = req.get_json()
                body = PushRequestBody(**req_body)
                logging.info(f'{aaId} pushed metrics for period : {body.start_time} - {body.end_time}')
                logging.info(req_body)
            except ValueError as e:
                logging.error(e)
                return azure.functions.HttpResponse(format_error("validation_error",str(e)), headers={'content-type':'application/json'})
            except Exception as e:
                logging.error(e)
                return azure.functions.HttpResponse(format_error("auth_error","Invalid credentials"), headers={'content-type':'application/json'}, status_code=400)
            try:
                account_discovery_metric(body)
                return azure.functions.HttpResponse('{"success":true,"message":"Successfully pushed metric"}',headers={'content-type':'application/json'}, status_code = 200)
            except RequestException as e:
                return azure.functions.HttpResponse(format_error("api_error",str(e)), headers={'content-type':'application/json'}, status_code=400)
        if api_type == 'report':
            try:
                claim = verify_and_decode_credentials(auth, 'AA')
                req_body = req.get_json()
                fiuId = claim['azp']
                logging.info(req_body)
                report_query = ReportRequestBody(**req_body)
                logging.info(f'{fiuId} pushed metrics for period : {report_query.duration} - {report_query.evaluate_at}')
                report_response = asyncio.run(get_report_async(report_query))
                return azure.functions.HttpResponse(report_response,headers={'content-type':'application/json'})
            except ValueError as e:
                return azure.functions.HttpResponse(format_error("validation_error",str(e)), headers={'content-type':'application/json'}, status_code=400)
            except Exception as e:
                logging.error(e)
                return azure.functions.HttpResponse(format_error("auth_error","Invalid credentials"), headers={'content-type':'application/json'}, status_code=400)
    else:
        return azure.functions.HttpResponse(
            "Invalid operation. Please use POST method on /api/push APIs.",
            status_code=400
        )
