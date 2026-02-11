import csv
import random

can_types = ["AAD", "AAY", "AMJ", "AMD", "AMP"]


def generate_csv(file_name, num_cans):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["uld_id", "uld_type", "current_weight", "weight", "status"])

        for i in range(num_cans):
            u_type = random.choice(can_types)
            u_id = f"{u_type}{random.randint(10000, 99999)}"
            c_weight = random.randint(1500, 4500)

            writer.writerow([u_id, u_type, c_weight, 2000.00, "Loaded"])


if __name__ == "__main__":
    generate_csv('new_inventory.csv', 100)
    print("CSV Manifest generated for manual import.")