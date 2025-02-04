from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse  
from pymongo import MongoClient
import shortuuid
# import os 

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://darius:aabbdd@url-shortener.31rzo.mongodb.net/?retryWrites=true&w=majority&appName=url-shortener"

client = MongoClient(MONGO_URI)
db = client['url_shortener']
collection = db['urls']


try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

app = FastAPI()



# Allow all origins for testing purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔓 Allow all origins (replace '*' with specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class URLRequest(BaseModel):
    original_url: str

@app.post("/shorten")
async def shorten_url(request: URLRequest):
    short_id = shortuuid.ShortUUID().random(length=6)
    collection.insert_one({"original_url": request.original_url, "short_id": short_id, "clicks": 0})
    # return short_id
    return {"short_url": f"http://localhost:8000/{short_id}"}

@app.get("/{short_id}")
async def redirect_to_url(short_id: str):
    url_data = collection.find_one({"short_id": short_id})
    if url_data:
        collection.update_one({"short_id": short_id}, {"$inc": {"clicks": 1}})
        # return {"original_url": url_data["original_url"]}
        return RedirectResponse(url=url_data["original_url"])
    raise HTTPException(status_code=404, detail="URL not found")

@app.get("/analytics/{short_id}")
async def get_analytics(short_id: str):
    url_data = collection.find_one({"short_id": short_id})
    if url_data:
        return {"original_url": url_data["original_url"], "clicks": url_data["clicks"]}
    raise HTTPException(status_code=404, detail="URL not found")
