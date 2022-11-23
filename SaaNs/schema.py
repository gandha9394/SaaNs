from pydantic import BaseModel
from typing import List, Dict, Union
from enum import Enum
# {
# start_time:""
# end_time:""
# fips:{
#   fipId:[{
#     "latency_ms": "",
#     "success_count": "",
#     "notFoundCount": "",
#     "event/category": "",
#     failure_count: "",
#     total_count: "",
#     latencyP90_ms: "",
#     latencyP95_ms: "",
#     latencyP50_ms: "",
#     }]
#   }
# }

class EventTypes(str, Enum):
    ACCOUNT_DISCOVERY = "FIP_ACCOUNT_DISCOVERY"

class FIPEventSchema(BaseModel):
    latency_ms: float
    success_count: int
    failure_count: int
    total_count: int 
    event: EventTypes
    latencyP90_ms: float
    latencyP95_ms: float
    latencyP50_ms: float

class FIPObjectSchema(BaseModel):
    __root__: Dict[str, List[FIPEventSchema]]

class RequestSchema(BaseModel):
    start_time: str
    end_time: str
    fips: FIPObjectSchema
    
class MetricEventTypes(BaseModel):
    pass
class MetricType(BaseModel):
    metric: MetricEventTypes
    timestamp: int
    value: Union[int, str, float]
