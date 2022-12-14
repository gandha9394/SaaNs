# generated by datamodel-codegen:
#   filename:  swagger.json
#   timestamp: 2022-11-28T05:22:46+00:00


from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Event(Enum):
    FIP_DISCOVERY = 'FIP_ACCOUNT_DISCOVERY'
    FIP_LINK_ACCOUNT = 'FIP_LINK_ACCOUNT'
    AA_USER_APPROVE_CONSENT = 'AA_USER_APPROVE_CONSENT'


class FipObject(BaseModel):
    name: Event = Field( example='100')
    fipId: str = Field( example='100')
    success_count: int = Field( example='100')
    failure_count: int = Field( example='100')
    total_count: int = Field( example='100')
    latency_ms: int = Field( example='100')
    latencyP90_ms: int = Field( example='100')
    latencyP95_ms: int = Field( example='100')
    latencyP50_ms: int = Field( example='100')
    class Config:  
        use_enum_values = True  


class ReportRequestBody(BaseModel):
    # TODO: Add validations
    duration: Optional[str] =  Field(None, example='12h30m')
    evaluate_at: Optional[str] = Field(None, example='2022-01-20T14:04:00.000Z')
    start_time: Optional[str] = Field(None, example='2022-01-20T13:04:00.000Z')
    end_time: Optional[str] = Field(None, example='2022-01-20T13:14:00.000Z')
    fipIds: Optional[List[str]] = Field(None, example=['FIP-ID1', 'FIP-ID2'])
    events: Optional[List[Event]] = Field(
        None, example=['FIP_ACCOUNT_DISCOVERY', 'FIP_LINK_ACCOUNT']
    )
    class Config:  
        use_enum_values = True  


class Event1(Enum):
    FIP_DISCOVERY = 'FIP_DISCOVERY'
    FIP_LINK_ACCOUNT = 'FIP_LINK_ACCOUNT'
    AA_USER_APPROVE_CONSENT = 'AA_USER_APPROVE_CONSENT'


class ReportResponseFIPObject(BaseModel):
    fipId: Optional[str] = Field(None, example='FIP-ID1')
    event: Optional[Event1] = None
    latency: Optional[int] = Field(None, example='100')
    successCount: Optional[int] = Field(None, example='100')
    failureCount: Optional[int] = Field(None, example='100')
    notFoundCount: Optional[int] = Field(None, example='100')
    totalCount: Optional[int] = Field(None, example='100')
    latency_p90: Optional[int] = Field(None, example='100')
    latency_p95: Optional[int] = Field(None, example='100')
    latency_p50: Optional[int] = Field(None, example='100')


# class Fips(BaseModel):
#     icici: Optional[List[FipObject]] = None
#     hdfc: Optional[List[FipObject]] = None


class PushRequestBody(BaseModel):
    # TODO: add validations
    start_time: Optional[str] = Field(None, example='2022-01-20T13:04:00.000Z')
    end_time: Optional[str] = Field(None, example='2022-01-20T13:14:00.000Z')
    events: Optional[List[FipObject]] = None


class ReportResponseBody(BaseModel):
    data: Optional[List[ReportResponseFIPObject]] = None
