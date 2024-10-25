import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openexcept import OpenExcept
from datetime import datetime, timedelta
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
    timestamp: datetime
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
                timestamp=exception.timestamp,
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
async def get_top_exception_groups(limit: int = 10, start_time: datetime = None, end_time: datetime = None):
    try:
        # Add logging to see what's being passed to the method
        logging.info(f"Fetching top exceptions groups with limit={limit}, start_time={start_time}, end_time={end_time}")
        
        # If start_time is not provided, set it to 24 hours ago
        if start_time is None:
            start_time = datetime.now() - timedelta(days=1)
        
        # Add a timeout of 30 seconds
        result = await asyncio.wait_for(
            asyncio.to_thread(grouper.get_top_exceptions, limit=limit, start_time=start_time, end_time=end_time),
            timeout=30.0
        )
        return JSONResponse(content=result)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        # Log the full exception details
        logging.exception("An error occurred while fetching top exceptions")
        raise HTTPException(status_code=500, detail=str(e))
