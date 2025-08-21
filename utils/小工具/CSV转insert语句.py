import csv
import os

from setuptools.command.egg_info import write_file

csv_file = '/tmp/area.csv'
insert_statements = []

with open(csv_file, 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # Skip the header row
    headers.append('created_by')
    headers.append('last_modified_by')
    headers.append('created_date')
    headers.append('last_modified_date')
    headerStr = ', '.join(headers)
    for row in csv_reader:
        if row:  # Ensure it's not an empty row
            values = ["'" + value + "'" if value else "''" for value in row]
            values.append("'system'")
            values.append("'system'")
            values.append("'2025-08-21 10:55:01'")
            values.append("'2025-08-21 10:55:01'")
            formatted_values = ', '.join(values)
            insert_statement = f"INSERT INTO sys_area ({headerStr}) VALUES ({formatted_values});"
            insert_statements.append(insert_statement)


# Now you have a list of all INSERT statements
# for statement in insert_statements:
#     print(statement)
# 脚本写入到文件中
fileName = '/tmp/area.sql'
if not os.path.exists(fileName):
    try:
        writeFile = open(fileName, 'a')
        writeFile.write('\n'.join(insert_statements))
    finally:
        writeFile.flush()
        writeFile.close()