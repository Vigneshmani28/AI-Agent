from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from taskpilot.api.v1.agent_controller import router as agent_router
import uvicorn


app = FastAPI(title="TaskPilot - Agentic AI Task Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router, prefix="/api/v1", tags=["Agent"])


@app.get("/health")
def health_status():
    return {"status": 200, "message": "TaskPilot is running 🚀"}


if __name__ == "__main__":
    uvicorn.run("taskpilot.main:app", host="localhost", port=8002, reload=True)
