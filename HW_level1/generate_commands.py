import random

options = ["angel", "A", "B", "C"]
for _ in range(100):
    argv_1 = random.choice(options)
    argv_2 = random.choice(options)
    while argv_2 == argv_1:  # Ensure argv_2 is not the same as argv_1
        argv_2 = random.choice(options)
    argv_3 = random.randint(1, 64)  # You can change the range as needed
    print(f"py app_transaction.py {argv_1} {argv_2} {argv_3}")
