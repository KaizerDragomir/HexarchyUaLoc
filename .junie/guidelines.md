This project is about adding Ukrainian localization to the PC game Hexarchy.

1. **Build/Configuration Instructions**:
- No manual run. There will be additional scripts to handle parsing.

2. **Structure of the project:**
- Outdated. Localization_WorkingCopy-resources.assets-3757.dat is the source file in CSV format, needed only if the mod is officially accepted.
- I2Languages-resources.assets-76790.json correct file with localization data (built/JSON format). Focus on this file for modding.
- Folder Scripts will contain scripts to parse the file and generate localization files.
- Folder `LocUI` will contain the TKinter GUI application for localization editing.
- Folder `language` contains subfolders for each language using its English name (e.g., 'Ukrainian').
- Inside each language folder:
    - `settings.json`: Configuration file for the language, used by scripts (e.g., `create_filler_json.py`).
    - 'Added': Contains the localization file with the new language added.
    - 'Override': Contains the localization file where the new language overrides English (used to bypass PlayFab limitations).
- Don't create any other files.

3. **Python guidelines**:
- Write as an experienced Python developer.
- Use Python 3.14.
- Use PEP8 guidelines.
- Don't comment except really necessary.
- Avoid external libraries unless they significantly simplify the script.
- In cases if some python script fails, try to handle the error gracefully and provide informative error messages.

4. **Testing Information**:
- Testing localization will be done manually. We will use the game's built-in localization tools and compare the output with expected results.

5. **Commiting policy**:
- All commits will be done manually or after user approval. 

6. **Other**:
- Always ask questions after the prompt if needed.

After testing:
- Delete all additional files that you created except `.junie/guidelines.md` and asked in prompts.
- Temporary files (like `last_session.json` or logs) should be ignored by VCS and removed after session.
