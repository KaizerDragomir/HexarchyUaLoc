import csv
import os

def create_filler():
    input_file = 'Localization_WorkingCopy-resources.assets-3757.dat'
    output_file = 'Localization_WorkingCopy-resources.assets-3757.dat_new'
    
    # We need to handle the first line specially if it has non-standard characters at the beginning
    with open(input_file, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
        
    # Find the first line break to separate header and data if needed, 
    # but csv module might handle it. 
    # Let's check the first few bytes for BOM or weird characters.
    
    with open(input_file, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    if not rows:
        return

    # Header is in rows[0]
    header = rows[0]
    if header[0].startswith('\x18\x00\x00\x00'):
        header[0] = header[0][4:]
        prefix = '\x18\x00\x00\x00'
    else:
        prefix = ''
    
    header.append('Ukrainian')
    
    # Process data rows
    for i in range(1, len(rows)):
        row = rows[i]
        # Ensure row has enough columns (at least 4 for English at index 3)
        if len(row) > 3:
            english_text = row[3]
            if english_text:
                row.append(f"NeedUA {english_text}")
            else:
                row.append("")
        else:
            # If row is shorter than expected (e.g. empty line or separator)
            # still add a column if it's not completely empty
            if any(row):
                row.append("")
            # If it's a completely empty row (like row 23), keep it as is or add empty col?
            # The issue says "Different languages are separated with coma. End of the localization are usually without coma."
            # Looking at row 23: ",,,,,,,,,,,,,," (14 commas, so 15 empty cols)
            # If I add Ukrainian, I should add another comma.
            if len(row) > 0:
                while len(row) < len(header) - 1:
                    row.append("")
                row.append("")

    header[0] = prefix + header[0]
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)

    # Replace original file
    os.replace(output_file, input_file)
    print("Ukrainian column added successfully.")

if __name__ == "__main__":
    create_filler()
