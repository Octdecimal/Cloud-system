# 組員
# B1129030 吳采庭
# B1129037 許德暉
import hashlib
import sys
from app_transaction import sha256_file
from app_transaction import block_folder
from app_transaction import initail_block
from app_transaction import create_new_block
from app_transaction import find_last_block

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app_checkChain.py <checker>")
        sys.exit(1)
    checker = sys.argv[1]
    
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
    print("All the blocks have been checked.")
    # add "angle, {checker}, 10" to the last block
    
    last_block = find_last_block(initail_block)
    last_block_path = block_folder + last_block
    with open(last_block_path, 'a') as f:
        f.write(f"\nangel, {checker}, 10")
        
    # if there are five transactions in the last block, create a new block
    create_new_block(block_folder, last_block)