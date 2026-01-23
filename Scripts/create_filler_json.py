import json
import os
import sys


def load_json(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        sys.exit(1)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)


def save_json(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving JSON: {e}")
        sys.exit(1)


def ensure_ukrainian_language(languages):
    for i, lang in enumerate(languages):
        if lang.get('Name') == 'Ukrainian':
            return i, False
    
    languages.append({
        "Name": "Ukrainian",
        "Code": "uk",
        "Flags": 0
    })
    return len(languages) - 1, True


def process_terms(terms, uk_index):
    updated_count = 0
    for term in terms:
        term_name = term.get('Term', "")
        lang_array = term.get('Languages', {}).get('Array', [])
        flags_array = term.get('Flags', {}).get('Array', [])
        
        # If the Ukrainian entry is missing or the array is too short
        if len(lang_array) <= uk_index:
            # Fill missing entries up to uk_index
            while len(lang_array) < uk_index:
                lang_array.append("")
                flags_array.append(0)
            
            # Add the Ukrainian translation
            if "FONT" in term_name:
                source_val = lang_array[7] if len(lang_array) > 7 else ""
                lang_array.append(source_val)
            else:
                english_val = lang_array[0] if len(lang_array) > 0 else ""
                lang_array.append(f"NeedUA {english_val}")
            
            flags_array.append(0)
            updated_count += 1
        else:
            # Entry exists, check if it needs correction (specifically for FONT terms)
            if "FONT" in term_name:
                current_uk = lang_array[uk_index]
                russian_val = lang_array[7] if len(lang_array) > 7 else ""
                
                # If it has NeedUA prefix or is different from Russian, update it
                if current_uk.startswith("NeedUA ") or current_uk != russian_val:
                    lang_array[uk_index] = russian_val
                    updated_count += 1
            
    return updated_count


def ensure_ukrainian_term(terms):
    if any(term.get('Term') == 'LANG/UKRAINIAN' for term in terms):
        return False
        
    insertion_idx = -1
    for i, term in enumerate(terms):
        if term.get('Term') == 'LANG/RUSSIAN':
            insertion_idx = i + 1
            break
    
    ukrainian_term = {
        "Term": "LANG/UKRAINIAN",
        "TermType": 0,
        "Languages": {
            "Array": [
                "Ukrainian", "Ukrainien", "Ukrainisch", "Ucraniano",
                "ウクライナ語", "우크라이나어", "Ukraiński", "Украинский",
                "Ucraniano", "乌克兰语", "烏克蘭語", "Українська"
            ]
        },
        "Flags": {
            "Array": [0] * 12
        },
        "Languages_Touch": {
            "Array": []
        }
    }
    
    if insertion_idx != -1:
        terms.insert(insertion_idx, ukrainian_term)
    else:
        terms.append(ukrainian_term)
    return True


def create_filler_json():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, '..', 'I2Languages-resources.assets-76790.json')
    
    data = load_json(input_file)
    source = data.get('mSource', {})
    languages = source.get('mLanguages', {}).get('Array', [])
    terms = source.get('mTerms', {}).get('Array', [])
    
    uk_index, lang_added = ensure_ukrainian_language(languages)
    updated_terms_count = process_terms(terms, uk_index)
    term_added = ensure_ukrainian_term(terms)
    
    if lang_added or updated_terms_count > 0 or term_added:
        save_json(input_file, data)
        print(f"Success: Added language: {lang_added}, "
              f"Updated terms: {updated_terms_count}, "
              f"Added LANG/UKRAINIAN: {term_added}")
    else:
        print("No changes needed. Ukrainian localization is up to date.")


if __name__ == "__main__":
    create_filler_json()
