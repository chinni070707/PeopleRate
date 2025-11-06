# Simple demo server without MongoDB dependency for testing
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

app = FastAPI(
    title="PeopleRate API - Demo",
    description="A people review platform similar to TrustPilot but for individuals",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Demo data
demo_people = [
    {
        "id": "1", 
        "full_name": "John Smith", 
        "company": "Microsoft", 
        "city": "Seattle", 
        "job_title": "Software Engineer",
        "average_rating": 4.8, 
        "total_reviews": 12
    },
    {
        "id": "2", 
        "full_name": "Jane Doe", 
        "company": "Google", 
        "city": "Mountain View", 
        "job_title": "Product Manager",
        "average_rating": 4.6, 
        "total_reviews": 8
    }
]

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/persons/search")
async def search_persons(q: str):
    """Demo search endpoint"""
    results = []
    for person in demo_people:
        if q.lower() in person["full_name"].lower() or \
           q.lower() in person.get("company", "").lower() or \
           q.lower() in person.get("city", "").lower():
            results.append(person)
    return results

@app.get("/docs")
async def get_docs():
    """API Documentation endpoint"""
    return {"message": "Visit /docs for interactive API documentation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)