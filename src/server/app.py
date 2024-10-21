import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openexcept import OpenExcept
from datetime import datetime
import logging
import asyncio
from fastapi.responses import JSONResponse

# Add this line to set up logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
grouper = OpenExcept(config_path=config_path)

class ExceptionInput(BaseModel):
    message: str
    type: str = "Unknown"
    timestamp: datetime = None
    context: dict = {}

class GroupResult(BaseModel):
    group_id: str

@app.post("/process", response_model=GroupResult)
async def process_exception(exception: ExceptionInput):
    try:
        # Add a timeout of 10 seconds
        group_id = await asyncio.wait_for(
            asyncio.to_thread(
                grouper.group_exception,
                message=exception.message,
                type_name=exception.type,
                timestamp=exception.timestamp or datetime.now(),
                **exception.context
            ),
            timeout=10.0,
        )
        return GroupResult(group_id=group_id)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top_exceptions")
async def get_top_exceptions(limit: int = 10, days: int = 1):
    try:
        # Add logging to see what's being passed to the method
        logging.info(f"Fetching top exceptions with limit={limit} and days={days}")
        
        # Add a timeout of 30 seconds
        result = await asyncio.wait_for(
            asyncio.to_thread(grouper.get_top_exceptions, limit=limit, days=days),
            timeout=30.0
        )
        return JSONResponse(content=result)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        # Log the full exception details
        logging.exception("An error occurred while fetching top exceptions")
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))