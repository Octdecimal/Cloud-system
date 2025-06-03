from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from upload import router as upload_router
from task_status import router as status_router
from network_discovery import start_discovery
from node_registry import add_node as register_node
from download import router as download_router
from network_discovery import router as node_usage_router

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://172.17.0.2:5173"],  # Allow requests from Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wrapped_add_node(ip, busy):
    register_node(ip, busy)

app.include_router(upload_router, prefix="/upload")
app.include_router(status_router)
app.include_router(download_router)
app.include_router(node_usage_router)

# Start background discovery
start_discovery(wrapped_add_node)