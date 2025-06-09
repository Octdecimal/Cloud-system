# 組員
# B1129030 吳采庭
# B1129037 許德暉
import sys
import hashlib

block_folder = "./"
initail_block = "0.txt"

def find_last_block(current_block):
    # read the second line of the file
    # if it is empty after "Next block: ", return current_block
    # if it is not empty, open the file and read the next block
    
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
    # Open the file in binary mode and compute the SHA-256 hash
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def create_new_block(block_folder, last_block):
    # create a new block with the sha256 of the last block
    # and the next block as None
    last_block_path = block_folder + last_block
    with open(last_block_path, 'r+') as f:
        lines = f.readlines()
        if len(lines) >= 7:
            # create a new block
            new_block = str(int(last_block.split(".")[0]) + 1) + ".txt"
            new_block_path = block_folder + new_block
            
            # update the last block to point to the new block
            f.seek(0)
            lines[1] = f"Next block: {new_block}\n"
            f.writelines(lines)
            f.truncate()
            
            sha = sha256_file(last_block_path)
            with open(new_block_path, 'w') as f_new:
                f_new.write(f"Sha256 of previous block: {sha}")
                f_new.write(f"\nNext block: None")
            print(f"New block created: {new_block_path}")
            
        else:
            print(f"New data added to block: {last_block}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python app_transaction.py <from> <to> <dollar_amount>")
        sys.exit(1)
    
    from_account = sys.argv[1]
    to_account = sys.argv[2]
    dollar_amount = float(sys.argv[3])
    # Check if dollar_amount is a valid number
    if dollar_amount <= 0:
        print("Error: dollar_amount must be a positive number")
        sys.exit(1)
    
    # find the last block
    last_block = find_last_block(initail_block)
    last_block_path = block_folder + last_block
    
    # add <from_account> <to_account> <dollar_amount> to the last block
    with open(last_block_path, 'a') as f:
        f.write(f"\n{from_account}, {to_account}, {dollar_amount}")
        
    # if there are five transactions in the last block, create a new block
    create_new_block(block_folder, last_block)