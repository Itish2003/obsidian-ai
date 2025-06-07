from fastapi import FastAPI
from .models.custom_models import RunRequest, Event
from typing import List

app = FastAPI()

@app.post("/run", response_model=List[Event])
async def run_endpoint(request: RunRequest):
    # TODO: Integrate with your OrchestratorAgent logic
    # For now, return a dummy response
    return [
        Event(type="text", content=f"Echo: {request.new_message}", is_final_response=True)
    ]