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
        self.sock.bind(('172.17.0.4', self.port)) #這是本節點的 IP

    def start(self):
        threading.Thread(target=self._listen).start()
        threading.Thread(target=self._send_messages).start()

    def _listen(self):
        while True:
            command, A_account, B_account, dollar_amount, peer= self.sock.recvfrom(1024)
            command = command.decode()
            A_account = A_account.decode()
            B_account = B_account.decode()
            dollar_amount = dollar_amount.decode()
            if command == "transaction" or "checkChain":
                transaction(A_account, B_account, dollar_amount)

    def _send_messages(self):
        while True:
            command, from_account, to_account, amount = input("Enter a command (checkMoney, checkLog, transaction, checkChain, checkAllChain): ")
            A_account, B_account, dollar_amount = run_command(command, from_account, to_account, amount)
            for peer in self.peers:
                self.sock.sendto(f"{command}, {A_account}, {B_account}, {dollar_amount}".encode(), peer)


def run_command(command, A_account, B_account, dollar_amount):
    if command == "checkMoney":
        return checkMoney(A_account)
    elif command == "checkLog":
        return checkLog(A_account)
    elif command == "transaction":
        return transaction(A_account, B_account, dollar_amount)
    elif command == "checkChain":
        return checkChain(A_account)
    elif command == "checkAllChain":
        return checkAllChain(A_account)


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
    return None, None, None
    
    
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
    
    return None, None, None


def transaction(from_addr, to_addr, dollar):
    from_account = from_addr
    to_account = to_addr
    dollar_amount = dollar
    if dollar_amount <= 0:
        print("Error: dollar_amount must be a positive number")
        return
    
    last_block = find_last_block(initail_block)
    last_block_path = block_folder + last_block
    
    with open(last_block_path, 'a') as f:
        f.write(f"\n{from_account}, {to_account}, {dollar_amount}")
        
    create_new_block(block_folder, last_block)
    return from_account, to_account, dollar_amount
    
    
def checkChain(checker):
    checker = checker
    
    pre_block = initail_block
    current_block = initail_block
    while current_block != "None":
        current_block_path = block_folder + current_block
        pre_block_path = block_folder + pre_block
        with open(current_block_path, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                print(f"Error: {current_block} inforamtion missing.")
                break
            if current_block != "0.txt":
                sha_in_file = lines[0].strip().split(": ")[1]
                sha = sha256_file(pre_block_path)
                if sha_in_file != sha:
                    print(f"Error: {pre_block} is not valid.")
                    print(f"sha256 of {pre_block} is {sha_in_file},\nbut the actual sha256 is {sha}.\n")
                    
                if len(lines) > 7:
                    print(f"Error: {current_block} has more than 5 transactions.")
            pre_block = current_block
            current_block = lines[1].strip().split(": ")[1]
    
    last_block = find_last_block(initail_block)
    last_block_path = block_folder + last_block
    with open(last_block_path, 'a') as f:
        f.write(f"\nangel, {checker}, 10")
        
    create_new_block(block_folder, last_block)
    return "angel", checker, 10


def last_block_check():
    current_block = initail_block
    last_block = find_last_block(current_block)
    return sha256_file(block_folder + last_block)


def checkAllChain(checker):
    checker = checker
    
    pre_block = initail_block
    current_block = initail_block
    corrupt = False
    while current_block != "None":
        current_block_path = block_folder + current_block
        pre_block_path = block_folder + pre_block
        with open(current_block_path, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                corrupt = True
                break
            if current_block != "0.txt":
                sha_in_file = lines[0].strip().split(": ")[1]
                sha = sha256_file(pre_block_path)
                if sha_in_file != sha:
                    corrupt = True
                    break
                if len(lines) > 7:
                    corrupt = True
                    break
            pre_block = current_block
            current_block = lines[1].strip().split(": ")[1]
    # code
    if corrupt:
        print(f"Error: {current_block} is not valid.")
    else:
        return last_block_check()


if __name__ == '__main__':
    port = 8001 #本節點的port 
    peers = [('172.17.0.2', 8001), ('172.17.0.3', 8001)]  #跟另外二個IP:8001 節點通信
    node = P2PNode(port, peers)
    node.start()

