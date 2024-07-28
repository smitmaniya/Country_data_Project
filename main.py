from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Optional, Union

app = FastAPI()

# MongoDB connection details
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.world_bank
collection = database.countries

# Pydantic model for the country data
class Country(BaseModel):
    Country: str
    Population: Optional[str] = None
    Life_Expectancy: Optional[Union[str, int]] = None

@app.get("/country/{country_name}", response_model=Country)
async def get_country_data(country_name: str):
    country = await collection.find_one({"Country": country_name})
    if country:
        # Ensure Population and Life_Expectancy are correctly formatted
        if "Population" in country and isinstance(country["Population"], int):
            country["Population"] = str(country["Population"])
        if "Life_Expectancy" in country and isinstance(country["Life_Expectancy"], int):
            country["Life_Expectancy"] = str(country["Life_Expectancy"])
        return Country(**country)
    else:
        raise HTTPException(status_code=404, detail="Country not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
