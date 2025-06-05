import threading, time
from task_status import get_ready_tasks, update_task_status
from node_registry import get_nodes, set_node_status
from task_assign import assign_task

def _schedule_loop():
   while True:
	   for task_id in get_ready_tasks():
		   # 選一個空閒節點
		   nodes = get_nodes(only_available=True)
		   if not nodes:
			   break
		   node_ip = nodes[0]    # 簡單起見：拿第一個
		   success = assign_task(task_id, node_ip)
		   if success:
			   set_node_status(node_ip, True)
			   update_task_status(task_id, "assigned", node_ip)
	   time.sleep(1)

def start_scheduler():
   thread = threading.Thread(target=_schedule_loop, daemon=True)
   thread.start()
