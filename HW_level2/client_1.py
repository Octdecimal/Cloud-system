import socket
import threading
import hashlib

block_folder = "./"
initail_block = "0.txt"


class P2PNode:
    def __init__(self, port, peers):
        self.port = port
        self.peers = peers
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('172.17.0.4', self.port))  # 本地IP
        self.sha_map = {}         # 儲存節點 SHA 值
        self.completed_nodes = set()  # 儲存已完成的節點
        self.checker = None       # 記錄誰發起驗證
        self.local_sha = None     # 本地 SHA
        self.node_id = ('172.17.0.4', self.port)

    def start(self):
        threading.Thread(target=self._listen).start()
        threading.Thread(target=self._send_messages).start()

    def _listen(self):
        while True:
            data, peer = self.sock.recvfrom(1024)
            parts = data.decode().split(', ')
            command = parts[0]

            if command in ["transaction", "checkChain"]:
                from_account = parts[1]
                to_account = parts[2]
                amount = float(parts[3])
                transaction(from_account, to_account, amount)
            elif command == "startCompare":
                self.checker = parts[1]
                self.local_sha = last_block_check()
                self.sha_map = {self.node_id: self.local_sha}
                self.completed_nodes = set()

                # broadcast 自己的 SHA 給所有人
                for p in self.peers:
                    self.sock.sendto(f"reportSha, {self.local_sha}".encode(), p)

            elif command == "reportSha":
                sha = parts[1]
                self.sha_map[peer] = sha

                if len(self.sha_map) == len(self.peers) + 1:  # 收齊所有 SHA
                    sha_counts = {}
                    for s in self.sha_map.values():
                        sha_counts[s] = sha_counts.get(s, 0) + 1
                    
                    majority_sha = max(sha_counts.items(), key=lambda x: x[1])

                    if majority_sha[1] > (len(self.peers) + 1) / 2:
                        if self.local_sha != majority_sha[0]:
                            print("Replacing local chain with majority chain!")
                            # 找到正確鏈的擁有者
                            for peer_node, sha in self.sha_map.items():
                                if sha == majority_sha[0] and peer_node != self.node_id:
                                    request_msg = "requestChain".encode()
                                    node.sock.sendto(request_msg, peer_node)
                                    break
                    else:
                        print("No consensus. System not trusted.")

                    # 廣播已完成比較
                    for p in self.peers:
                        self.sock.sendto("compareDone".encode(), p)

            elif command == "compareDone":
                self.completed_nodes.add(peer)
                if len(self.completed_nodes) == len(self.peers):
                    if self.checker:
                        print(f"Consensus complete. Rewarding {self.checker}")
                        transaction("angel", self.checker, 100)
            
            elif command == "requestChain":
                # 將整條鏈打包回傳
                all_blocks = []
                current_block = initail_block
                while current_block != "None":
                    block_path = block_folder + current_block
                    with open(block_path, 'r') as f:
                        all_blocks.append(f"{current_block}<<<{f.read()}")
                    with open(block_path, 'r') as f:
                        lines = f.readlines()
                        current_block = lines[1].strip().split(": ")[1]

                chain_data = "@@@".join(all_blocks)
                self.sock.sendto(f"sendChain, {chain_data}".encode(), peer)

            elif command == "sendChain":
                raw_chain = data.decode().split(", ", 1)[1]
                blocks = raw_chain.split("@@@")
                
                # 清空原本的鏈
                import os
                for file in os.listdir(block_folder):
                    if file.endswith(".txt"):
                        os.remove(os.path.join(block_folder, file))

                for block in blocks:
                    if "<<<" not in block:
                        continue
                    filename, content = block.split("<<<", 1)
                    with open(block_folder + filename, 'w') as f:
                        f.write(content)
                print("Chain has been synchronized with majority.")


    def _send_messages(self):
        while True:
            raw = input("Enter a command (checkMoney, checkLog, transaction, checkChain, checkAllChain): ")
            parts = raw.strip().split()
            if len(parts) < 1:
                continue
            command = parts[0]
            A_account = parts[1] if len(parts) > 1 else None
            B_account = parts[2] if len(parts) > 2 else None
            amount = float(parts[3]) if len(parts) > 3 else None
            
            if command == "checkMoney":
                checkMoney(A_account)
                
            elif command == "checkLog":
                checkLog(A_account)
                
            elif command == "transaction":
                A_account, B_account, amount = transaction(A_account, B_account, amount)
                for peer in self.peers:
                    self.sock.sendto(f"transaction, {A_account}, {B_account}, {amount}".encode(), peer)

            elif command == "checkChain":
                A_account, B_account, amount = checkChain(A_account)
                for peer in self.peers:
                    self.sock.sendto(f"checkChain, {A_account}, {B_account}, {amount}".encode(), peer)
            
            elif command == "checkAllChain":
                self.checker = parts[1] if len(parts) > 1 else "unknown"
                if local_chain_is_valid():
                    self.local_sha = last_block_check()
                    for peer in self.peers:
                        self.sock.sendto(f"startCompare, {self.checker}".encode(), peer)
                    # 自己也執行 reportSha 邏輯
                    self._listen_local_sha()
                else:
                    print("Local chain is invalid.")

    def _listen_local_sha(self):
        self.sha_map = {self.node_id: self.local_sha}
        for p in self.peers:
            self.sock.sendto(f"reportSha, {self.local_sha}".encode(), p)


def find_last_block(current_block):
    current_block_path = block_folder + current_block
    with open(current_block_path, 'r') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return current_block
        next_block = lines[1].strip().split(": ")[1]
        if next_block == "None" or next_block == "\n":
            return current_block
        else:
            return find_last_block(next_block)


def sha256_file(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def create_new_block(block_folder, last_block):
    last_block_path = block_folder + last_block
    with open(last_block_path, 'r+') as f:
        lines = f.readlines()
        if len(lines) >= 7:
            new_block = str(int(last_block.split(".")[0]) + 1) + ".txt"
            new_block_path = block_folder + new_block
            
            f.seek(0)
            lines[1] = f"Next block: {new_block}\n"
            f.writelines(lines)
            f.truncate()
            
            sha = sha256_file(last_block_path)
            with open(new_block_path, 'w') as f_new:
                f_new.write(f"Sha256 of previous block: {sha}")
                f_new.write(f"\nNext block: None")


def checkMoney(goal):
    account = goal
    balance = 0
    current_block = initail_block

    while current_block != "None":
        block_path = block_folder + current_block
        with open(block_path, 'r') as f:
            lines = f.readlines()
            for line in lines[2:]:  # Skip metadata
                parts = [p.strip() for p in line.strip().split(',')]
                if len(parts) == 3:
                    sender, receiver, amount = parts
                    try:
                        amount = float(amount)
                    except ValueError:
                        continue
                    if sender == "angel" and receiver == account:
                        balance += amount
                    elif sender == account:
                        balance -= amount
                    elif receiver == account:
                        balance += amount
            current_block = lines[1].strip().split(": ")[1]

    print(f"Account '{account}' balance: {balance}")
    
    
def checkLog(goal):
    account = goal
    current_block = initail_block

    print(f"Transaction logs for account '{account}':\n")

    while current_block != "None":
        block_path = block_folder + current_block
        with open(block_path, 'r') as f:
            lines = f.readlines()
            for line in lines[2:]:  # Skip first 2 lines (metadata)
                parts = [p.strip() for p in line.strip().split(',')]
                if len(parts) == 3:
                    sender, receiver, amount = parts
                    if sender == account or receiver == account:
                        print(f"{current_block}: {sender} -> {receiver} : {amount}")
            current_block = lines[1].strip().split(": ")[1]


def transaction(from_addr, to_addr, dollar):
    from_account = from_addr
    to_account = to_addr
    dollar_amount = dollar
    if dollar_amount <= 0.0:
        print("Error: dollar_amount must be a positive number")
        return
    
    last_block = find_last_block(initail_block)
    last_block_path = block_folder + last_block
    
    with open(last_block_path, 'a') as f:
        f.write(f"\n{from_account}, {to_account}, {dollar_amount}")
        
    create_new_block(block_folder, last_block)
    return from_account, to_account, dollar_amount
    
def local_chain_is_valid():
    pre_block = initail_block
    current_block = initail_block
    errorCode = 0
    while current_block != "None":
        current_path = block_folder + current_block
        pre_path = block_folder + pre_block
        with open(current_path, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                return errorCode + 1, current_path, None, None
            if current_block != "0.txt":
                sha_in_file = lines[0].strip().split(": ")[1]
                sha = sha256_file(pre_path)
                if sha_in_file != sha:
                    return errorCode + 2, pre_block, sha_in_file, sha
                if len(lines) > 7:
                    return errorCode + 3, current_path, None, None
        pre_block = current_block
        current_block = lines[1].strip().split(": ")[1]
    return errorCode, None, None, None

    
def checkChain(checker):
    checker = checker
    errorCode, error_block, sha_in_file, sha = local_chain_is_valid()
    
    if errorCode == 0:
        last_block = find_last_block(initail_block)
        last_block_path = block_folder + last_block
        with open(last_block_path, 'a') as f:
            f.write(f"\nangel, {checker}, 10")
            
        create_new_block(block_folder, last_block)
        return "angel", checker, 10
    elif errorCode == 1:
        print(f"Error: {error_block} inforamtion missing.")
    elif errorCode == 2:
        print(f"Error: {error_block} is not valid.")
        print(f"sha256 of {error_block} is {sha_in_file},\nbut the actual sha256 is {sha}.")
    elif errorCode == 3:
        print(f"Error: {error_block} has more than 5 transactions.")
        
    return "angel", checker, 10


def last_block_check():
    current_block = initail_block
    last_block = find_last_block(current_block)
    return sha256_file(block_folder + last_block)


def checkAllChain(checker):
    checker = checker
    
    errorCode, current_block = local_chain_is_valid()
    # code
    if errorCode != 0:
        print(f"Error: {current_block} is not valid.")
    return "angel", checker, 100


if __name__ == '__main__':
    port = 8001 #本節點的port 
    peers = [('172.17.0.2', 8001), ('172.17.0.3', 8001)]  #跟另外二個IP:8001 節點通信
    node = P2PNode(port, peers)
    node.start()

