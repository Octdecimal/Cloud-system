discovered_nodes = {}  # ip -> {busy: bool}

def add_node(ip: str, busy: bool = False):
    discovered_nodes[ip] = {"busy": busy}

def set_node_status(ip: str, busy: bool):
    if ip in discovered_nodes:
        discovered_nodes[ip]["busy"] = busy

def get_nodes(only_available=True):  # 只返回可用的節點
    if only_available:
        return [ip for ip, info in discovered_nodes.items() if not info["busy"]]
    return list(discovered_nodes.keys())
