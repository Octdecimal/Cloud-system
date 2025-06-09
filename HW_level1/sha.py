import hashlib

def sha256_file(file_path):
    # Open the file in binary mode and compute the SHA-256 hash
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

# Example usage
file_path = "./0.txt"
print(f"SHA-256 hash of the file: {sha256_file(file_path)}")