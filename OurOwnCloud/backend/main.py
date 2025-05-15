from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from upload import router as upload_router
from task_status import router as status_router
from task_status import all_tasks_search
from network_discovery import start_discovery, get_local_ip
from node_registry import add_node as register_node
from download import router as download_router

app = FastAPI()
ip = get_local_ip()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http:{ip}:5173"],  # Allow requests from Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wrapped_add_node(ip, busy):
    register_node(ip, busy)

app.include_router(upload_router, prefix="/upload")
app.include_router(status_router)
app.include_router(download_router)

# Start background discovery
start_discovery(wrapped_add_node)
all_tasks_search()