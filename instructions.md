fastapi dev ./app/fastapi_server.py 

streamlit run /Users/pruthvirajadhav/code/AI assignment/WebChatAgents/app/st_ui.py 

streamlit run --no-reload st_ui.py 

streamlit run st_ui.py

streamlit run ./frontend/streamlit_app.py 
docker compose up --build

fastapi dev ./app/main.py & streamlit run ./frontend/streamlit_app.py 
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload & streamlit run ./frontend/streamlit_app.py 