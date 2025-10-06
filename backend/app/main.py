import uvicorn
from fastapi import FastAPI

# Initialize the FastAPI application
app = FastAPI(title="Company Happiness Index API")


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "service": "company-happiness-backend"}


# Use this if you want to run the app directly (for local development)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
