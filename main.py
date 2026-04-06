from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
import datetime as DT
from datetime import datetime
import sqlite3
import logging
from database import init_db
from fastapi.middleware.cors import CORSMiddleware
from classes.batteryData import BatteryData
from classes.energyConsumptionData import EnergyConsumptionData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialized")

def get_db():
    con = sqlite3.connect("sunmate.db", check_same_thread=False)
    cur = con.cursor()
    try:
        yield con, cur
    finally:
        con.close()

@app.get("/battery/soc")
async def root(db=Depends(get_db)):
    con, cur = db
    cur.execute("SELECT * FROM batteryData ORDER BY timestamp DESC LIMIT 1;")
    row = cur.fetchone()
    logger.info("Battery SOC requested: %s%%", row[1])
    return {"timestamp": row[0], "soc": row[1]}

@app.post("/battery/daily")
async def create_daily_data(item: list[BatteryData], db=Depends(get_db)):
    con, cur = db

    for daily_data in item:
        cur.execute(
            "INSERT INTO batteryData VALUES(?, ?)",
            (daily_data.timestamp.isoformat(), daily_data.soc)
        )

    con.commit()

    lowest_soc = min(daily_data.soc for daily_data in item)
    highest_soc = max(daily_data.soc for daily_data in item)
    soc_difference = highest_soc - lowest_soc

    logger.info("Battery daily data posted: %d entries", len(item))
    return {
        "lowest_soc": lowest_soc,
        "highest_soc": highest_soc,
        "soc_difference": soc_difference
    }

@app.get("/energy/consumption")
async def get_energy_consumption(db=Depends(get_db)):
    con, cur = db
    cur.execute("SELECT * FROM energyConsumptionData ORDER BY timestamp ASC;")
    rows = cur.fetchall()

    result = []
    for row in rows:
        timestamp = datetime.fromisoformat(row[0])
        result.append({
            "hour": timestamp.strftime("%H:%M"),
            "consumption_kwh": row[1]
        })

    logger.info("Energy consumption requested: %d entries", len(result))
    return result

@app.post("/energy/consumption")
async def create_energy_consumption(item: EnergyConsumptionData, db=Depends(get_db)):
    con, cur = db
    cur.execute(
        "INSERT INTO energyConsumptionData VALUES(?, ?)",
        (item.timestamp.isoformat(), item.consumption_kwh)
    )
    con.commit()
    logger.info("Energy consumption posted: %s kWh", item.consumption_kwh)
    return {"message": "Energiforbrug registreret", "consumption_kwh": item.consumption_kwh}

