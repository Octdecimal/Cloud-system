import socket
import threading
import hashlib
import os
import time

block_folder = "./"
initail_block = "0.txt"


class P2PNode:
    def __init__(self, port, peers):
        self.port = port
        self.peers = peers
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('172.17.0.2', self.port))  # 本地IP
        self.sha_map = {}         # 儲存節點 SHA 值
        self.completed_nodes = set()  # 儲存已完成的節點
        self.checker = None       # 記錄誰發起驗證
        self.local_sha = None     # 本地 SHA
        self.node_id = ('172.17.0.2', self.port)
        self.chain_lock = threading.Lock()
        self.timeout = 60
        self.recvChain = False  # 是否收到鏈的標記

    def start(self):
        threading.Thread(target=self._listen).start()
        threading.Thread(target=self._send_messages).start()
        threading.Thread(target=self._consensus).start()
        threading.Thread(target=self._waitAllSha).start()
        
    def _consensus(self):
        while True:
            time.sleep(1)
            self.timeout -= 1
            if len(self.completed_nodes) == len(self.peers) + 1:
                if self.checker:
                    with self.chain_lock:
                        errorCode, _, _, _ = local_chain_is_valid()
                        if errorCode == 0:
                            print(f"+ Local chain is valid.")
                        else:
                            print(f"! Local chain is unvalid. Error code: {errorCode}")
                        
                        print(f"+ Consensus complete. Rewarding {self.checker}")
                        transaction("angel", self.checker, 100.0)
                        # 清空已完成的節點與 SHA 值
                        self.completed_nodes.clear()
                        self.sha_map.clear()
                        self.checker = None
                        self.local_sha = None
                        self.timeout = 60
            if self.timeout <= 0:
                self.completed_nodes.clear()
                self.sha_map.clear()
                self.checker = None
                self.local_sha = None
                self.timeout = 60
                
    def _waitAllSha(self):
        while True:
            time.sleep(1)
            if len(self.sha_map) == len(self.peers) + 1:  # 收齊所有 SHA
                sha_counts = {}
                for s in self.sha_map.values():
                    sha_counts[s] = sha_counts.get(s, 0) + 1
                
                majority_sha = max(sha_counts.items(), key=lambda x: x[1])

                if majority_sha[1] > (len(self.peers) + 1) / 2:
                    if self.local_sha != majority_sha[0]:
                        print(f"+ Majority sha is {majority_sha[0]}")
                        print(f"+ Local sha is {self.local_sha}")
                        print("+ Replacing local chain with majority chain!")
                        # 找到正確鏈的擁有者
                        for peer_node, sha in self.sha_map.items():
                            if sha == majority_sha[0] and peer_node != self.node_id:
                                request_msg = "requestChain".encode()
                                node.sock.sendto(request_msg, peer_node)
                                break
                    else:
                        print(f"+ Local sha is already the majority sha: {self.local_sha}")
                        print("+ No need to replace local chain.")
                        # 廣播已完成比較
                        self.completed_nodes.add(self.node_id)
                        for p in self.peers:
                            self.sock.sendto("compareDone".encode(), p)
                else:
                    print("+ No consensus. System not trusted.")
                    # 廣播已完成比較
                    self.completed_nodes.add(self.node_id)
                    for p in self.peers:
                        self.sock.sendto("compareDone".encode(), p)

    def _listen(self):
        while True:
            data, peer = self.sock.recvfrom(32767)
            parts = data.decode().split(', ')
            command = parts[0]

            if command in ["transaction", "checkChain"]:
                print(f"+ Received {command} from {peer}")
                from_account = parts[1]
                to_account = parts[2]
                amount = float(parts[3])
                transaction(from_account, to_account, amount)
                
            elif command == "startCompare":
                print(f"+ Received startCompare from {peer}")
                self.checker = parts[1]
                self.local_sha = last_block_check()
                self.sha_map = {self.node_id: self.local_sha}
                self.completed_nodes = set()
                
                # broadcast 自己的 SHA 給所有人
                for p in self.peers:
                    self.sock.sendto(f"reportSha, {self.local_sha}".encode(), p)

            elif command == "reportSha":
                print(f"+ Received reportSha from {peer}")
                sha = parts[1].strip()
                if peer not in self.sha_map:
                    self.sha_map[peer] = sha

            elif command == "compareDone":
                print(f"+ Received compareDone from {peer}")
                self.timeout = 60
                self.completed_nodes.add(peer)
            
            elif command == "requestChain":
                print(f"+ Received requestChain from {peer}")
                current_block = initail_block
                while current_block != "None":
                    block_path = block_folder + current_block
                    with open(block_path, 'r') as f:
                        content = f.read()
                    msg = f"sendBlock, {current_block}<<<{content}"
                    self.sock.sendto(msg.encode(), peer)

                    # 讀下一個 block
                    with open(block_path, 'r') as f:
                        lines = f.readlines()
                        current_block = lines[1].strip().split(": ")[1]

                # 全部區塊送完，發送結尾標誌
                self.sock.sendto("sendBlock, End".encode(), peer)

            elif command == "sendBlock":
                print(f"+ Received sendBlock from {peer}")
                content = data.decode().split(", ", 1)[1]

                with self.chain_lock:
                    if content == "End":
                        print("+ Chain has been synchronized with majority.")
                        self.completed_nodes.add(self.node_id)
                        self.recvChain = False
                        for p in self.peers:
                            self.sock.sendto("compareDone".encode(), p)
                    else:
                        if not self.recvChain:
                            self.recvChain = True
                            # 第一次進來時，清空本地鏈
                            for file in os.listdir(block_folder):
                                if file.endswith(".txt"):
                                    os.remove(os.path.join(block_folder, file))

                        if "<<<" not in content:
                            print("! Invalid block format received.")
                            return

                        filename, filedata = content.split("<<<", 1)
                        with open(block_folder + filename, 'w') as f:
                            f.write(filedata)

    def _send_messages(self):
        print("Enter a command (checkMoney, checkLog, transaction, checkChain, checkAllChain): ")
        while True:
            raw = input()
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
                print(f"+ Transaction: {A_account} -> {B_account} : {amount}")
                for peer in self.peers:
                    self.sock.sendto(f"transaction, {A_account}, {B_account}, {amount}".encode(), peer)

            elif command == "checkChain":
                A_account, B_account, amount = checkChain(A_account)
                for peer in self.peers:
                    self.sock.sendto(f"checkChain, {A_account}, {B_account}, {amount}".encode(), peer)
            
            elif command == "checkAllChain":
                self.checker = parts[1] if len(parts) > 1 else "unknown"
                errorCode, _, _, _ = local_chain_is_valid()
                if errorCode == 0:
                    self.local_sha = last_block_check()
                    for peer in self.peers:
                        self.sock.sendto(f"startCompare, {self.checker}".encode(), peer)
                    # 自己也執行 reportSha 邏輯
                    self._listen_local_sha()
                else:
                    print("! Local chain is invalid.")
            else:
                print("! Unknown command. Please try again.")

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
        
    elif errorCode == 1:
        print(f"Error: {error_block} inforamtion missing.")
        
    elif errorCode == 2:
        print(f"Error: {error_block} is not valid.")
        print(f"sha256 of {error_block} is {sha_in_file},\nbut the actual sha256 is {sha}.")
        
    elif errorCode == 3:
        print(f"Error: {error_block} has more than 5 transactions.")
        
    return "angel", checker, 10.0


def last_block_check():
    current_block = initail_block
    last_block = find_last_block(current_block)
    return sha256_file(block_folder + last_block)


if __name__ == '__main__':
    port = 8001 #本節點的port 
    peers = [('172.17.0.4', 8001), ('172.17.0.3', 8001)]  #跟另外二個IP:8001 節點通信
    node = P2PNode(port, peers)
    node.start()

