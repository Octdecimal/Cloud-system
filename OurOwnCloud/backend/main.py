from fastapi import FastAPI
from upload import router as upload_router
from task_status import router as status_router
from network_discovery import start_discovery
from node_registry import add_node as register_node
from notify import router as notify_router


app = FastAPI()

def wrapped_add_node(ip, busy):
    register_node(ip, busy)

app.include_router(upload_router, prefix="/upload")
app.include_router(status_router, prefix="/status")
app.include_router(notify_router, prefix="/notify")

# Start background discovery
start_discovery(wrapped_add_node)