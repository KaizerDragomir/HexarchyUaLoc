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


def load_settings(language):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(script_dir, '..', 'language', language, 'settings.json')
    if not os.path.exists(settings_path):
        print(f"Error: Settings for language '{language}' not found at {settings_path}")
        sys.exit(1)
    try:
        with open(settings_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        sys.exit(1)


def ensure_language(languages, settings):
    lang_name = settings['Name']
    for i, lang in enumerate(languages):
        if lang.get('Name') == lang_name:
            return i, False
    
    languages.append({
        "Name": lang_name,
        "Code": settings['Code'],
        "Flags": settings['Flags']
    })
    return len(languages) - 1, True


def get_lang_index(languages, lang_name):
    for i, lang in enumerate(languages):
        if lang.get('Name') == lang_name:
            return i
    return -1


def process_terms(terms, lang_index, settings, languages):
    updated_count = 0
    filler_prefix = settings.get('FillerPrefix', "Need ")
    copy_from = settings.get('CopyFromIndex', 0)
    
    font_copy_lang = settings.get('FontCopyFromLanguage', "Russian")
    font_copy_from = get_lang_index(languages, font_copy_lang)
    
    if font_copy_from == -1:
        print(f"Warning: Fallback font language '{font_copy_lang}' not found. Using English (0).")
        font_copy_from = 0
    
    for term in terms:
        term_name = term.get('Term', "")
        lang_array = term.get('Languages', {}).get('Array', [])
        flags_array = term.get('Flags', {}).get('Array', [])
        
        if len(lang_array) <= lang_index:
            while len(lang_array) < lang_index:
                lang_array.append("")
                flags_array.append(0)
            
            if "FONT" in term_name:
                source_val = lang_array[font_copy_from] if len(lang_array) > font_copy_from else ""
                lang_array.append(source_val)
            else:
                english_val = lang_array[copy_from] if len(lang_array) > copy_from else ""
                lang_array.append(f"{filler_prefix}{english_val}")
            
            flags_array.append(0)
            updated_count += 1
        else:
            if "FONT" in term_name:
                current_lang_val = lang_array[lang_index]
                source_val = lang_array[font_copy_from] if len(lang_array) > font_copy_from else ""
                
                if current_lang_val.startswith(filler_prefix) or current_lang_val != source_val:
                    lang_array[lang_index] = source_val
                    updated_count += 1
            
    return updated_count


def ensure_lang_term(terms, settings):
    lang_term_name = settings['Term']
    if any(term.get('Term') == lang_term_name for term in terms):
        return False
        
    insertion_idx = -1
    for i, term in enumerate(terms):
        if term.get('Term') == 'LANG/RUSSIAN':
            insertion_idx = i + 1
            break
    
    new_term = {
        "Term": lang_term_name,
        "TermType": 0,
        "Languages": {
            "Array": settings['Translations']
        },
        "Flags": {
            "Array": [0] * len(settings['Translations'])
        },
        "Languages_Touch": {
            "Array": []
        }
    }
    
    if insertion_idx != -1:
        terms.insert(insertion_idx, new_term)
    else:
        terms.append(new_term)
    return True


def create_filler_json():
    if len(sys.argv) < 2:
        print("Usage: python create_filler_json.py <LanguageName>")
        print("Example: python create_filler_json.py Ukrainian")
        sys.exit(1)
    
    language = sys.argv[1]
    settings = load_settings(language)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, '..', 'I2Languages-resources.assets-76790.json')
    
    data = load_json(input_file)
    source = data.get('mSource', {})
    languages = source.get('mLanguages', {}).get('Array', [])
    terms = source.get('mTerms', {}).get('Array', [])
    
    lang_index, lang_added = ensure_language(languages, settings)
    updated_terms_count = process_terms(terms, lang_index, settings, languages)
    term_added = ensure_lang_term(terms, settings)
    
    if lang_added or updated_terms_count > 0 or term_added:
        save_json(input_file, data)
        print(f"Success for {language}: Added language: {lang_added}, "
              f"Updated terms: {updated_terms_count}, "
              f"Added {settings['Term']}: {term_added}")
    else:
        print(f"No changes needed for {language}. Localization is up to date.")


if __name__ == "__main__":
    create_filler_json()
