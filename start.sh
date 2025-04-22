#!/bin/bash
set -e

# Check the first argument to determine which service to run
if [ "$1" = "api" ]; then
    echo "Starting FastAPI service..."
    exec uvicorn app.main:app --host $HOST --port $PORT
elif [ "$1" = "streamlit" ]; then
    echo "Starting Streamlit service..."
    exec streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
else
    echo "Please specify either 'api' or 'streamlit' as the first argument"
    exit 1
fi