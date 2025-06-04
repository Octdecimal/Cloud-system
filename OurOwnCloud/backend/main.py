from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 各功能模組的 router
from upload             import router as upload_router
from task_status        import router as status_router
from download           import router as download_router
from network_discovery  import router as node_usage_router, start_discovery
from assign_controller  import router as assign_router
from scheduler          import start_scheduler

# 節點註冊函式
from node_registry      import add_node as register_node

app = FastAPI(title="Distributed Music Mashup Service")

# 全域 CORS 設定（開發階段可暫時 allow *，生產再鎖定）
app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],      # 或 ["http://localhost:5173"]
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
		)

# 將各 router 掛上去
app.include_router(upload_router,      prefix="/upload", tags=["Upload"])
app.include_router(status_router,      tags=["Task Status"])
app.include_router(download_router,    tags=["Download"])
app.include_router(node_usage_router,  tags=["Node Usage"])
app.include_router(assign_router,      prefix="/task", tags=["Task Assignment"])

def _node_discovered_callback(ip: str, busy: bool):
	"""
	network_discovery 探測到新節點或節點狀態更新時呼叫，
	把它註冊到 node_registry 裡。
	"""
	register_node(ip, busy)

@app.on_event("startup")
def on_startup():
	# 啟動後台的節點廣播偵測與任務排程器
	start_discovery(_node_discovered_callback)
	start_scheduler()

if __name__ == "__main__":
	import uvicorn
	# 本機測試用
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
