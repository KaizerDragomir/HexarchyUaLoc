import json
import os
import shutil
from datetime import datetime

class LocalizationModel:
    def __init__(self, project_root):
        self.project_root = project_root
        self.data = None
        self.file_path = None
        self.languages = []
        self.terms = []
        self.is_modified = False
        self.target_lang_index = -1
        self.reference_lang_indices = [0]  # Default English (usually index 0)
        self.category_list = []
        self.selected_categories = set()
        self.settings = {}

    def load_settings(self, language_name):
        """Loads the language-specific settings.json file."""
        settings_path = os.path.join(self.project_root, 'language', language_name, 'settings.json')
        if os.path.exists(settings_path):
            try:
                # Using utf-8-sig to handle possible BOM
                with open(settings_path, 'r', encoding='utf-8-sig') as f:
                    self.settings = json.load(f)
                return True
            except (json.JSONDecodeError, IOError) as e:
                # Log or handle specific errors if needed
                print(f"Error loading settings for {language_name}: {e}")
        return False

    def load_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.file_path = file_path
            self._parse_data()
            self.is_modified = False
            return True, ""
        except Exception as e:
            return False, str(e)

    def _parse_data(self):
        """Extracts languages, terms, and categories from the loaded JSON data."""
        if not self.data:
            return

        source = self.data.get('mSource', {})
        self.languages = source.get('mLanguages', {}).get('Array', [])
        self.terms = source.get('mTerms', {}).get('Array', [])
        
        # Extract unique categories
        categories = set()
        for term_obj in self.terms:
            term_name = term_obj.get('Term', '')
            if '/' in term_name:
                categories.add(term_name.split('/')[0])
            else:
                categories.add("UNCATEGORIZED")
        
        self.category_list = sorted(list(categories))
        # Default to selecting all categories if not already set
        if not self.selected_categories:
            self.selected_categories = set(self.category_list)
        else:
            # Refresh selected categories to only include existing ones
            self.selected_categories &= categories

    def save_json(self, file_path=None):
        if file_path:
            self.file_path = file_path
        
        if not self.file_path:
            return False, "No file path specified"

        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            self.is_modified = False
            return True, ""
        except Exception as e:
            return False, str(e)

    def create_backup(self):
        if not self.file_path or not os.path.exists(self.file_path):
            return False, "No file to backup"
        
        backup_path = f"{self.file_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        try:
            shutil.copy2(self.file_path, backup_path)
            return True, backup_path
        except Exception as e:
            return False, str(e)

    def update_translation(self, term_index, lang_index, new_value):
        """Updates the translation for a specific term and language."""
        try:
            if not (0 <= term_index < len(self.terms)):
                return False, "Term index out of range"
                
            term = self.terms[term_index]
            lang_array = term.get('Languages', {}).get('Array', [])
            
            if 0 <= lang_index < len(lang_array):
                if lang_array[lang_index] != new_value:
                    lang_array[lang_index] = new_value
                    self.is_modified = True
                return True, ""
            return False, "Language index out of range"
        except Exception as e:
            return False, str(e)

    def get_term_data(self, index):
        if 0 <= index < len(self.terms):
            return self.terms[index]
        return None

    def get_translation(self, term_index, lang_index):
        """Retrieves the translation for a specific term and language."""
        term = self.get_term_data(term_index)
        if term:
            lang_array = term.get('Languages', {}).get('Array', [])
            if 0 <= lang_index < len(lang_array):
                return lang_array[lang_index]
        return ""

    def is_term_translated(self, term_index, lang_index):
        """Checks if a term is considered fully translated (not empty and no filler prefix)."""
        translation = self.get_translation(term_index, lang_index)
        if not translation:
            return False
        
        filler_prefix = self.settings.get('FillerPrefix', "")
        if filler_prefix and translation.startswith(filler_prefix):
            return False
            
        return True
