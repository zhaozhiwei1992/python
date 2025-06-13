import openpyxl

wb = openpyxl.load_workbook('/tmp/月周计划模板.xlsx', False)
sheet = wb['周计划']
insert_statements = []

with open(csv_file, 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)  # Skip the header row
    headerStr = ', '.join(headers)
    for row in csv_reader:
        if row:  # Ensure it's not an empty row
            values = ["'" + value + "'" if value else "''" for value in row]
            formatted_values = ', '.join(values)
            insert_statement = f"INSERT INTO czb_gfa_formula ({headerStr}) VALUES ({formatted_values});"
            insert_statements.append(insert_statement)


# Now you have a list of all INSERT statements
for statement in insert_statements:
    print(statement)