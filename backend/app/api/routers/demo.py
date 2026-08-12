from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/demo", tags=["demo"])

# Global state to act as our "Live Source"
DEMO_STATE = {
    "records": [
        {
            "id": "scheme_01",
            "name": "Housing Grant",
            "income_limit": 300000,
            "status": "active"
        }
    ]
}

class MutateRequest(BaseModel):
    income_limit: int

@router.get("/source")
async def get_demo_source():
    """
    Returns the current state of the demo reality.
    """
    return DEMO_STATE

@router.post("/mutate")
async def mutate_demo_source(req: MutateRequest):
    """
    Changes the demo reality.
    """
    DEMO_STATE["records"][0]["income_limit"] = req.income_limit
    return {"status": "success", "new_state": DEMO_STATE}
