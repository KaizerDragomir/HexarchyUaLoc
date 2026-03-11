# LocUI TKinter Application Guidelines

This application is designed to provide a graphical user interface for managing the localization JSON file (`I2Languages-resources.assets-76790.json`), reducing the risk of manual errors.

## System structure
- **Root Folder**: Contains the main application files and scripts.
- **LocUI Folder**: Houses the main application scripts and GUI components.
- **Scripts Folder**: Contains utility scripts for data processing and validation.
- **language Folder**: Stores language-specific data and translations. This application will work with this data.
- Check quidelines.md for more details. Keep this md up to date with the main changes.

## Application Structure
- **Root Folder**: `LocUI`
- **Main Script**: `LocUI/launchUI.py`
- **Scripts**: use scripts from the root/Scripts folder for utility work
- **Modules**: (Optional) Additional modules for logic/GUI components should be placed within the `LocUI` folder. 

## Key Features
1. **Language Selection**: Ability to load the target JSON file from the `language` folder.
    - **Target**: Always edit language-specific JSONs (e.g., `language/Ukrainian/Added/...`). Do NOT edit the root JSON directly (it's for Steam sync).
2. **Create New Language**: Ability to create a new language file with the correct structure.
    - **Settings**: window to set default language settings according to guidelines.
    - **Setting acceptance**: Every setting must be set. There must be no empty fields.
    - **Language File**: after language settings are set, the application will create a new language file with the correct structure.
3. **Master-Detail Layout**:
    - **Sidebar/List**: A list of all terms (or filtered terms).
    - **Editing Area**: Shows the selected term, its category, and translation fields.
    - **Reference Languages**: Display other languages (English by default, others selectable) side-by-side for reference. These are **read-only**.
4. **Search and Filter**: 
    - Search for terms, specific translations in the current language, or reference language translations.
    - Filter terms by **Category**. Use a **checkbox group** for multiple category selection.
5. **Editing**: Interface to update the translation for a given term.
    - **Editable**: Only the translation field is editable. Terms and reference languages are locked.
    - **Placeholders**: Ensure all placeholders (e.g., `{0}`, `<b>`) are preserved during editing.
    - Hit Enter to validate and save the translation in memory.
    - Hit Escape to cancel the translation change.
6. **Validation**: Built-in validation to ensure the JSON structure remains intact and follows the expected schema.
7. **Sync**: Ability to trigger the sync/filler scripts from within the UI (if applicable).
    - **Current Status**: Sync to DAT is currently broken; for now, the app only saves to JSON.
8. **Save**: Overwrite the current language-specific JSON file with the updated translations.
9. **Override**: override is a process when we're changing another language with the selected language in a JSON file. We need it to bypass Playfab validation.
    - **Confirmation**: Before overwriting, prompt the user for confirmation.
    - **Backup**: Create a backup of the original file before overwriting.
10. **Exit**: Close the application gracefully.
11. **Not saved warning**: If the user tries to exit or load/create another language without saving, prompt for confirmation.

## Term Categories
Terms in the localization JSON follow the pattern `CATEGORY/TERM_NAME` (e.g., `CARD_MISC/USECIVICSRELIGIONSTOOLTIP`).
- **Category**: The prefix before the first forward slash (`/`). In the example, `CARD_MISC` is the category.
- **Filtering**: The UI should allow users to select or search by these categories to focus on specific groups of terms (e.g., all cards, all UI labels, etc.).
Localization is considered as "full" if there is no language prefix left.

## Technical Requirements
- **Framework**: TKinter (standard library).
- **Python Version**: 3.14.
- **Style**: Follow PEP8, minimal comments, robust error handling.
- **Dependencies**: Use standard library as much as possible.

## User Interface Guidelines
- Keep the design simple and functional.
- Provide clear feedback for save/load operations.
- Display errors via message boxes.

## Desired Menu Structure
- **File**
    - New Language
    - Load Language
    - Save (Ctrl+S)
    - Override 
    - Exit
- **Edit**
    - Search Term... (Ctrl+F)
    - Filter by Category...
    - Hide Translated Terms checkbox (Ctrl+T)
    - Hide Empty Categories checkbox (Ctrl+E)
    - Next Result (F3)
    - Previous Result (Shift+F3)
- **Tools**
    - Run Validator
    - Sync json with DAT
- **Help**
    - Guidelines
    - About
