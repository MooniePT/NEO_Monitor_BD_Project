
import csv
import os

path = r"c:\Users\Carlos\Documents\GitHub\NEO_Monitor_BD_Project\NEO_Monitoring\docs\neo.csv"

with open("header_dump.txt", "w", encoding="utf-8") as out:
    if not os.path.exists(path):
        out.write("File not found.")
        exit()

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        out.write(f"HEADERS: {reader.fieldnames}\n")
        
        try:
            row = next(reader)
            out.write(f"FIRST ROW: {row}\n")
            out.write(f"Has 'diameter'? {'diameter' in row}\n")
        except StopIteration:
            out.write("Empty CSV.\n")
