
from pydantic import BaseModel, Field
import datetime as DT
    
class BatteryData(BaseModel):
    timestamp: DT.datetime
    soc: int = Field(..., ge=0, le=100)