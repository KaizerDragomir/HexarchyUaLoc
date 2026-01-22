import json
import os
import sys

def create_filler_json():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The JSON file is one level up from the Scripts folder
    input_file = os.path.join(script_dir, '..', 'I2Languages-resources.assets-76790.json')
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        sys.exit(1)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)

    try:
        source = data.get('mSource', {})
        languages = source.get('mLanguages', {}).get('Array', [])
        
        # Check if Ukrainian already exists
        if any(lang.get('Name') == 'Ukrainian' for lang in languages):
            print("Ukrainian localization already exists. Skipping.")
            return

        # 1. Add Ukrainian as a last new option in the language list mLanguages
        languages.append({
            "Name": "Ukrainian",
            "Code": "uk",
            "Flags": 0
        })

        # 2. Copy english translation with prefix NeedUA for all the terms
        terms = source.get('mTerms', {}).get('Array', [])
        for term in terms:
            lang_array = term.get('Languages', {}).get('Array', [])
            flags_array = term.get('Flags', {}).get('Array', [])
            
            english_val = ""
            if len(lang_array) > 0:
                english_val = lang_array[0]
            
            lang_array.append(f"NeedUA {english_val}")
            
            # Usually Flags array size matches Languages array size
            flags_array.append(0)

        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print("Ukrainian localization filler added successfully.")

    except Exception as e:
        print(f"Error processing data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_filler_json()
