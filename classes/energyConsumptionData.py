from pydantic import BaseModel
import datetime as DT


class EnergyConsumptionData(BaseModel):
    timestamp: DT.datetime
    consumption_kwh: float