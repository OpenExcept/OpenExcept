#!/bin/bash

# Initialize the database
python -m src.openexcept.scripts.init_db

# Start the application
uvicorn src.server.app:app --host 0.0.0.0 --port 8000 --workers 4 --reload 