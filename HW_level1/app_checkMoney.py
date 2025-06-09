# 組員
# B1129030 吳采庭
# B1129037 許德暉
import sys
from app_transaction import block_folder, initail_block

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app_checkMoney.py <account>")
        sys.exit(1)

    account = sys.argv[1]
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