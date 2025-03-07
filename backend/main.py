from fastapi import FastAPI, HTTPException
import uvicorn
from hospital_agent import run_agent
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class HospitalQueryInput(BaseModel):
    text: str

class HospitalQueryOutput(BaseModel):
    input: str
    output: str
    intermediate_steps: List[str] = []  # Default empty list to avoid 'field required' error

app = FastAPI(
    title="Hospital Chatbot",
    description="Endpoints for a hospital system graph RAG chatbot",
)

@app.post("/hospital_agent")
def query_hospital_agent(query: HospitalQueryInput) -> HospitalQueryOutput:
    # Get the response from the agent
    response = run_agent(query.text)  
    
    # Process the response based on its format
    if isinstance(response, dict):
        # If it's a dict, extract the output
        if "output" in response:
            output_text = str(response["output"])
        else:
            output_text = str(response)
            
        # Extract intermediate steps if available
        steps = []
        if "intermediate_steps" in response:
            for action, observation in response["intermediate_steps"]:
                steps.append(f"Tool: {action.tool}, Input: {action.tool_input}, Result: {str(observation)}")
    else:
        output_text = str(response)
        steps = []
    
    return HospitalQueryOutput(
        input=query.text,
        output=output_text,
        intermediate_steps=steps
    )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)