import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import sys
from models import LocalizationModel

# Add root folder to sys.path to access Scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class LocApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hexarchy Localization Editor")
        self.geometry("1200x800")
        
        # Consistent project root
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model = LocalizationModel(self.project_root)
        self.filtered_indices = []
        self.current_selection_index = -1
        self.ref_text_widgets = []  # Store references to reference text widgets
        
        self.setup_ui()
        self._create_menu()
        self._bind_shortcuts()

    def setup_ui(self):
        """Initializes the main user interface components."""
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self._setup_sidebar()
        self._setup_editor()

    def _setup_sidebar(self):
        """Initializes the left sidebar with search and term list."""
        self.sidebar = tk.Frame(self.paned_window, width=300)
        self.sidebar.pack_propagate(False)
        self.paned_window.add(self.sidebar)

        search_frame = tk.LabelFrame(self.sidebar, text="Search & Filter")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.apply_filters())
        tk.Entry(search_frame, textvariable=self.search_var).pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(search_frame, text="Filter by Category...", command=self.open_category_filter).pack(fill=tk.X, padx=5, pady=2)
        
        self.hide_translated_var = tk.BooleanVar(value=False)
        tk.Checkbutton(search_frame, text="Hide Translated (Ctrl+T)", variable=self.hide_translated_var, 
                       command=self.apply_filters).pack(anchor=tk.W, padx=5)
        
        self.term_listbox = tk.Listbox(self.sidebar)
        self.term_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.term_listbox.bind("<<ListboxSelect>>", self.on_term_select)

    def _setup_editor(self):
        """Initializes the right editor pane with details and reference languages."""
        self.editor_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.editor_frame)
        
        # Term details
        details_frame = tk.LabelFrame(self.editor_frame, text="Term Details")
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(details_frame, text="Term:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.term_name_label = tk.Label(details_frame, text="", font=("Arial", 10, "bold"))
        self.term_name_label.grid(row=0, column=1, sticky=tk.W)
        
        tk.Label(details_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.category_label = tk.Label(details_frame, text="")
        self.category_label.grid(row=1, column=1, sticky=tk.W)

        # Main translation edit area
        edit_frame = tk.LabelFrame(self.editor_frame, text="Translation (Target Language)")
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.translation_text = tk.Text(edit_frame, wrap=tk.WORD, height=10)
        self.translation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.translation_text.bind("<Return>", self.save_current_translation)
        self.translation_text.bind("<Escape>", self.cancel_translation_edit)

        # Reference language scrollable area
        self.ref_frame = tk.LabelFrame(self.editor_frame, text="Reference Languages")
        self.ref_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.ref_canvas = tk.Canvas(self.ref_frame)
        self.ref_scrollbar = ttk.Scrollbar(self.ref_frame, orient="vertical", command=self.ref_canvas.yview)
        self.ref_inner_frame = tk.Frame(self.ref_canvas)
        
        self.ref_inner_frame.bind(
            "<Configure>",
            lambda e: self.ref_canvas.configure(scrollregion=self.ref_canvas.bbox("all"))
        )
        self.ref_canvas.create_window((0, 0), window=self.ref_inner_frame, anchor="nw")
        self.ref_canvas.configure(yscrollcommand=self.ref_scrollbar.set)
        
        self.ref_canvas.pack(side="left", fill="both", expand=True)
        self.ref_scrollbar.pack(side="right", fill="y")

    def _create_menu(self):
        menubar = tk.Menu(self)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Language", command=self.new_language)
        file_menu.add_command(label="Load Language", command=self.load_language)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Override", command=self.override_language)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Search Term...", accelerator="Ctrl+F", command=lambda: self.sidebar.focus_set())
        edit_menu.add_command(label="Filter by Category...", command=self.open_category_filter)
        edit_menu.add_checkbutton(label="Hide Translated Terms", variable=self.hide_translated_var, accelerator="Ctrl+T")
        edit_menu.add_separator()
        edit_menu.add_command(label="Reference Languages...", command=self.select_reference_languages)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Run Validator", command=self.run_validator)
        tools_menu.add_command(label="Sync json with DAT", command=self.run_sync_dat)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Guidelines", command=lambda: messagebox.showinfo("Guidelines", "Check .junie/locui.md"))
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Hexarchy Localization Tool v0.1"))
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)

    def _bind_shortcuts(self):
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-t>", lambda e: self.toggle_hide_translated())

    def toggle_hide_translated(self):
        self.hide_translated_var.set(not self.hide_translated_var.get())
        self.apply_filters()

    def load_language(self):
        if self.model.is_modified:
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Load anyway?"):
                return
        
        languages_dir = os.path.join(self.project_root, 'language')
        if not os.path.exists(languages_dir):
            os.makedirs(languages_dir, exist_ok=True)
            messagebox.showinfo("No Languages", "No language directories found.")
            return

        available_languages = []
        for d in os.listdir(languages_dir):
            full_path = os.path.join(languages_dir, d)
            if os.path.isdir(full_path):
                # Check for standard location
                json_path = os.path.join(full_path, 'Added', 'I2Languages-resources.assets-76790.json')
                if os.path.exists(json_path):
                    available_languages.append((d, json_path))
        
        if not available_languages:
            messagebox.showinfo("No Languages", "No language JSON files found in language/*/Added/ folders.")
            return

        # Selection Dialog
        dialog = tk.Toplevel(self)
        dialog.title("Select Language")
        dialog.geometry("300x400")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Select existing language:", font=("Arial", 10, "bold")).pack(pady=10)
        
        listbox = tk.Listbox(dialog, font=("Arial", 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for lang, path in available_languages:
            listbox.insert(tk.END, lang)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                lang_name, file_path = available_languages[idx]
                success, error = self.model.load_json(file_path)
                if success:
                    self._post_load_actions()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", f"Failed to load: {error}")
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="Load", command=on_select, width=10).pack(side=tk.LEFT, padx=30)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=10).pack(side=tk.RIGHT, padx=30)
        
        # Double-click to load
        listbox.bind("<Double-Button-1>", lambda e: on_select())

    def _post_load_actions(self):
        # Determine language name from path
        parts = self.model.file_path.split(os.sep)
        if 'language' in parts:
            lang_idx = parts.index('language')
            if lang_idx + 1 < len(parts):
                lang_name = parts[lang_idx + 1]
                self.model.load_settings(lang_name)
        
        # Determine target language index
        if self.model.settings.get('Name'):
            for i, lang in enumerate(self.model.languages):
                if lang.get('Name') == self.model.settings['Name']:
                    self.model.target_lang_index = i
                    break
        
        if self.model.target_lang_index == -1:
            self.model.target_lang_index = len(self.model.languages) - 1
            
        self.update_ref_langs_ui()
        self.apply_filters()
        self.title(f"Hexarchy Localization Editor - {os.path.basename(self.model.file_path)}")

    def update_ref_langs_ui(self):
        """Rebuilds the reference language display area based on current selections."""
        for widget in self.ref_inner_frame.winfo_children():
            widget.destroy()
        
        self.ref_text_widgets = []
        for idx in self.model.reference_lang_indices:
            lang_name = self.model.languages[idx]['Name']
            tk.Label(self.ref_inner_frame, text=f"{lang_name}:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
            
            ref_text = tk.Text(self.ref_inner_frame, wrap=tk.WORD, height=4, state=tk.DISABLED, bg="#f0f0f0")
            ref_text.pack(fill=tk.X, expand=True, padx=5, pady=2)
            self.ref_text_widgets.append((idx, ref_text))

    def apply_filters(self):
        """Filters the term list based on search string and selected categories."""
        search_term = self.search_var.get().lower()
        hide_translated = self.hide_translated_var.get()
        
        self.filtered_indices = []
        self.term_listbox.delete(0, tk.END)
        
        # Batch insert for better performance
        terms_to_add = []
        for i, term_obj in enumerate(self.model.terms):
            term_name = term_obj.get('Term', '')
            
            # Category filter
            cat = term_name.split('/')[0] if '/' in term_name else "UNCATEGORIZED"
            if cat not in self.model.selected_categories:
                continue
            
            if search_term and search_term not in term_name.lower():
                continue
                
            if hide_translated:
                if self.model.is_term_translated(i, self.model.target_lang_index):
                    continue
            
            self.filtered_indices.append(i)
            terms_to_add.append(term_name)
        
        if terms_to_add:
            self.term_listbox.insert(tk.END, *terms_to_add)

    def on_term_select(self, event):
        """Handles term selection from the listbox, updating the editor and references."""
        # Auto-save current translation if selection changes
        if self.current_selection_index != -1:
            self.save_current_translation()

        selection = self.term_listbox.curselection()
        if not selection:
            self.current_selection_index = -1
            return
            
        index = self.filtered_indices[selection[0]]
        self.current_selection_index = index
        term_obj = self.model.get_term_data(index)
        
        # Update Details
        self.term_name_label.config(text=term_obj.get('Term', ''))
        cat = "UNCATEGORIZED"
        if '/' in term_obj.get('Term', ''):
            cat = term_obj.get('Term', '').split('/')[0]
        self.category_label.config(text=cat)
        
        # Update Editor
        self.translation_text.delete("1.0", tk.END)
        self.translation_text.insert("1.0", self.model.get_translation(index, self.model.target_lang_index))
        
        # Update References
        self._update_reference_texts(index)

    def _update_reference_texts(self, term_index):
        """Updates the content of the reference language text widgets."""
        for lang_idx, text_widget in self.ref_text_widgets:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", self.model.get_translation(term_index, lang_idx))
            text_widget.config(state=tk.DISABLED)

    def save_current_translation(self, event=None):
        if self.current_selection_index == -1:
            return "break"
            
        new_val = self.translation_text.get("1.0", tk.END).strip()
        self.model.update_translation(self.current_selection_index, self.model.target_lang_index, new_val)
        
        # If "Hide Translated" is active, we should update the list
        if self.hide_translated_var.get():
            self.apply_filters()
            
        return "break" # Prevent newline

    def cancel_translation_edit(self, event=None):
        if self.current_selection_index == -1:
            return
        self.on_term_select(None)

    def save_file(self):
        if not self.model.data:
            return
        success, error = self.model.save_json()
        if success:
            messagebox.showinfo("Success", "File saved successfully.")
        else:
            messagebox.showerror("Error", f"Failed to save: {error}")

    def run_validator(self):
        if not self.model.file_path:
            messagebox.showwarning("Warning", "Please load a language file first.")
            return
            
        import subprocess
        script_path = os.path.join(self.project_root, 'Scripts', 'validator.py')
        try:
            result = subprocess.run([sys.executable, script_path, self.model.file_path], capture_output=True, text=True)
            output = result.stdout + result.stderr
            
            top = tk.Toplevel(self)
            top.title("Validation Results")
            top.geometry("600x400")
            
            text = tk.Text(top, wrap=tk.WORD)
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text.insert(tk.END, output)
            text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run validator: {e}")

    def run_sync_dat(self):
        messagebox.showinfo("Sync to DAT", "Sync to DAT is currently broken (as per guidelines). For now, the app only saves to JSON.")

    def new_language(self):
        top = tk.Toplevel(self)
        top.title("New Language Wizard")
        top.geometry("400x500")
        
        fields = [
            ("Name", "Ukrainian"),
            ("Code", "uk"),
            ("Flags", 0),
            ("Term", "LANG/UKRAINIAN"),
            ("FillerPrefix", "NeedUA "),
            ("CopyFromIndex", 0),
            ("FontCopyFromLanguage", "English")
        ]
        
        entries = {}
        for i, (label, default) in enumerate(fields):
            tk.Label(top, text=label).pack(padx=10, pady=2)
            entry = tk.Entry(top)
            entry.insert(0, default)
            entry.pack(padx=10, pady=2, fill=tk.X)
            entries[label] = entry
            
        def create():
            settings = {label: entry.get().strip() for label, entry in entries.items()}
            if any(not v for v in settings.values()):
                messagebox.showerror("Error", "All fields are required.")
                return

            # enforce integer types for specific fields
            for key in ("Flags", "CopyFromIndex"):
                try:
                    settings[key] = int(settings.get(key, 0))
                except (ValueError, TypeError):
                    messagebox.showerror("Error", f"{key} must be an integer.")
                    return
            
            # Additional logic to create folder and settings.json
            # and run create_filler_json.py
            try:
                lang_name = settings['Name']
                lang_dir = os.path.join(self.project_root, 'language', lang_name)
                os.makedirs(lang_dir, exist_ok=True)
                
                settings_path = os.path.join(lang_dir, 'settings.json')
                # Add default translations for the LANG term
                settings['Translations'] = [lang_name] * 12 # Simplified
                
                with open(settings_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                
                import subprocess
                script_path = os.path.join(self.project_root, 'Scripts', 'create_filler_json.py')
                result = subprocess.run([sys.executable, script_path, lang_name], capture_output=True, text=True)
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"Language {lang_name} created. Loading it now...")
                    top.destroy()
                    
                    # Automatically load the newly created language file
                    added_file = os.path.join(lang_dir, 'Added', 'I2Languages-resources.assets-76790.json')
                    if os.path.exists(added_file):
                        success, error = self.model.load_json(added_file)
                        if success:
                            self._post_load_actions()
                        else:
                            messagebox.showerror("Error", f"Failed to load new language: {error}")
                else:
                    messagebox.showerror("Error", f"Failed to create filler JSON: {result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

        tk.Button(top, text="Create", command=create).pack(pady=20)

    def override_language(self):
        if not self.model.file_path:
            return
            
        if not messagebox.askyesno("Confirm Override", "This will override English translations with your current language to bypass PlayFab limitations. Continue?"):
            return
            
        success, backup_path = self.model.create_backup()
        if not success:
            messagebox.showerror("Error", f"Failed to create backup: {backup_path}")
            return
            
        # Implementation of override logic:
        # 1. Target is English (index 0)
        # 2. Source is self.model.target_lang_index
        count = 0
        for i, term_obj in enumerate(self.model.terms):
            source_val = self.model.get_translation(i, self.model.target_lang_index)
            if source_val:
                self.model.update_translation(i, 0, source_val)
                count += 1
        
        # Save to a new folder 'Override'
        lang_name = self.model.settings.get('Name', 'Unknown')
        override_dir = os.path.join(self.project_root, 'language', lang_name, 'Override')
        os.makedirs(override_dir, exist_ok=True)
        
        output_file = os.path.join(override_dir, os.path.basename(self.model.file_path))
        success, error = self.model.save_json(output_file)
        
        if success:
            messagebox.showinfo("Success", f"Override complete! {count} terms updated. Saved to: {output_file}")
        else:
            messagebox.showerror("Error", f"Failed to save override file: {error}")

    def select_reference_languages(self):
        if not self.model.languages:
            return
            
        top = tk.Toplevel(self)
        top.title("Select Reference Languages")
        
        vars = []
        for i, lang in enumerate(self.model.languages):
            var = tk.BooleanVar(value=(i in self.model.reference_lang_indices))
            cb = tk.Checkbutton(top, text=lang['Name'], variable=var)
            cb.pack(anchor=tk.W, padx=10, pady=2)
            vars.append((i, var))
            
        def apply():
            self.model.reference_lang_indices = [i for i, var in vars if var.get()]
            self.update_ref_langs_ui()
            if self.current_selection_index != -1:
                self._update_reference_texts(self.current_selection_index)
            top.destroy()
            
        def select_all():
            for _, var in vars: var.set(True)
            
        def select_none():
            for _, var in vars: var.set(False)

        btn_frame = tk.Frame(top)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Select All", command=select_all).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Select None", command=select_none).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Accept", command=apply).pack(side=tk.RIGHT, padx=5)

    def open_category_filter(self):
        if not self.model.category_list:
            return
            
        top = tk.Toplevel(self)
        top.title("Filter by Category")
        top.geometry("400x500")
        
        # Search bar in filter
        filter_search_var = tk.StringVar()
        tk.Entry(top, textvariable=filter_search_var).pack(fill=tk.X, padx=5, pady=5)
        
        # Action Buttons at the bottom (packed first with side=BOTTOM)
        btn_frame = tk.Frame(top)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        def apply():
            self.model.selected_categories = {cat for cat, var in vars.items() if var.get()}
            self.apply_filters()
            top.destroy()
            
        def select_all():
            for var in vars.values(): var.set(True)
            
        def select_none():
            for var in vars.values(): var.set(False)

        tk.Button(btn_frame, text="Check all", command=select_all).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Uncheck all", command=select_none).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Accept", command=apply).pack(side=tk.RIGHT, padx=5, pady=5)

        # Scrollable area for checkboxes
        canvas = tk.Canvas(top)
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        vars = {}
        for cat in self.model.category_list:
            var = tk.BooleanVar(value=(cat in self.model.selected_categories))
            cb = tk.Checkbutton(scroll_frame, text=cat, variable=var)
            cb.pack(anchor=tk.W)
            vars[cat] = var
            
        def on_filter_search(*args):
            s = filter_search_var.get().lower()
            for cb in scroll_frame.winfo_children():
                if s in cb.cget("text").lower():
                    cb.pack(anchor=tk.W)
                else:
                    cb.pack_forget()
                    
        filter_search_var.trace_add("write", on_filter_search)

    def on_exit(self):
        if self.model.is_modified:
            if not messagebox.askyesno("Exit", "Unsaved changes. Exit anyway?"):
                return
        self.destroy()

if __name__ == "__main__":
    app = LocApp()
    app.mainloop()
