from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ai.agent import generate_insight

router = APIRouter(prefix="/ai")


@router.get("/insights")
def get_insights():
    try:
        insight = generate_insight()
        return JSONResponse(content={"status": "success", "insight": insight})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
