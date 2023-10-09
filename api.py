from fastapi import FastAPI, Header
from pymongo import MongoClient



# Create a FastAPI instance
app = FastAPI()

# Create a PyMongo client and connect to MongoDB database
client = MongoClient("mongodb+srv://<username>:<password>@https://api.artdatabanken.se/species-observation-system/v1/api/ApiInfo?retryWrites=true&w=majority")
db = client.api/ApiInfo
collection = db.<collection>

@app.get("/data")
async def get_data(api_key: str = Header(None)):
    if api_key != "YOUR_API_KEY":
        return {"error": "Invalid API Key"}
    data = []
    for document in collection.find():
        data.append(document)
    return data
