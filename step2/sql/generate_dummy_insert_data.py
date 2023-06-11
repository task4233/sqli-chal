from faker import Faker
from uuid import uuid4

generator = Faker(["ja_JP"])
output_file_name = "1_insert_dummy_data.sql"

with open(output_file_name, "w") as f:
    for i in range(30):
        query = f'INSERT INTO users (name, key, is_admin) VALUES ("{generator.name()}", "{str(uuid4())}", "0");\n'
        f.writelines(query)
    f.writelines(
        "INSERT INTO users (name, key, is_admin) VALUES ('super_admin_314159', '1bea2d55-48fc-4ae4-a75f-9b4021fcb9a8', '1')\n"
    )
