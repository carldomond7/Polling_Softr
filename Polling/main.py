from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import time

app = FastAPI()

# Add CORS middleware to allow requests from your Softr page
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://deshawn582.preview.softr.app"],  # Allow your Softr domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.post("/poll-webhook/")
async def poll_webhook(request: Request):
    # Extract the webhook URL from the incoming JSON body
    data = await request.json()
    print(f"Received webhook_url: {data}")
    webhook_url = data.get("webhook_url")

    # If no webhook URL is provided, return an error
    if not webhook_url:
        raise HTTPException(status_code=400, detail="No webhook URL provided.")

    max_attempts = 10  # Maximum number of polling attempts
    attempts = 0
    delay = 5  # Delay in seconds between polling attempts

    while attempts < max_attempts:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(webhook_url)  # Poll the provided URL

            if response.status_code == 200:
                return response.json()  # Return the JSON body once 200 OK is received
            else:
                print(f"Attempt {attempts + 1}: Received {response.status_code}, retrying...")
                attempts += 1
                time.sleep(delay)  # Wait before the next attempt

        except httpx.RequestError as exc:
            print(f"Error polling webhook URL: {exc}")
            attempts += 1
            time.sleep(delay)

    # If the polling times out, return an error
    raise HTTPException(status_code=408, detail="Timeout waiting for webhook result after multiple attempts.")
