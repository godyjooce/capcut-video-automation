import pyautogui
import pyperclip
import time
import os
import random
import re
import json
# import subprocess # REMOVED: No longer needed for external script
# import sys # REMOVED: No longer needed for sys.executable
from pynput import keyboard # ADDED: for internal key press tracking
# import requests # REMOVED: for Pexels API, no longer used

# --- SETTINGS ---
CAPCUT_TEMPLATE_NAME = "auto.capcut"
PROMPT_FILE = "promt.txt" # Using original filename, assuming user wants it
USED_PROMPTS_FILE = "used_prompts.txt" # Using original filename
AUDIO_FOLDER = "audio" # AUDIO AND PHOTOS WILL BE HERE
OUTPUT_FOLDER = "output_videos"
COORDINATES_FILE = "coordinates.json"
# TOCHKI_SCRIPT_NAME = "tochki.py" # REMOVED: Helper script no longer used

# --- NEW PHOTO SETTINGS (API REMOVED) ---
# PEXELS_API_KEY = "..." # REMOVED: Pexels API is no longer used
# PHOTOS_FOLDER = "photos.video" # THIS VARIABLE IS NO LONGER ACTIVELY USED, PHOTOS ARE EXPECTED IN AUDIO_FOLDER
# PHOTOS_LOG_FILE = "used_photos_log.txt" # REMOVED: Log for Pexels photos, no longer used

# MINIMAL DELAYS (RISKY!) - YOU CAN INCREASE IF UNSTABLE
DELAY_MINIMAL = 0.3
DELAY_UI_RESPONSE = 0.5 # UI response time (menus, etc.)
DELAY_WINDOW_APPEAR = 0.8 # Window appearance time (dialogs, palettes)
DELAY_PROCESSING = 1.5 # Processing time (import, replace)
EXPORT_WAIT_TIME = 15 # Export wait time
DRAG_DURATION = 1.0 # Element drag time

# --- CAPCUT ELEMENT COORDINATES (Default values, taken from last request) ---
# IMPORTANT: If coordinates.json file exists, it will take precedence!
coordinates = {
    "TEXT_ELEMENT_ON_TIMELINE_X": 351,
    "TEXT_ELEMENT_ON_TIMELINE_Y": 1043,
    "TEXT_BOX_IN_INSPECTOR_X": 2215,
    "TEXT_BOX_IN_INSPECTOR_Y": 157,
    "TEXT_COLOR_PICKER_ICON_X": 2229,
    "TEXT_COLOR_PICKER_ICON_Y": 431,
    "TEXT_CHOSEN_COLOR_X": 2272,
    "TEXT_CHOSEN_COLOR_Y": 716,
    "EXISTING_AUDIO_TRACK_X": 1007,
    "EXISTING_AUDIO_TRACK_Y": 192,
    "CONFIRM_DELETE_AUDIO_BUTTON_X": 1211,
    "CONFIRM_DELETE_AUDIO_BUTTON_Y": 794,
    "MEDIA_TAB_X": 60,
    "MEDIA_TAB_Y": 55,
    "IMPORT_BUTTON_X": 202, # Used for both audio and photos
    "IMPORT_BUTTON_Y": 103,
    "WINDOWS_DIALOG_SEARCH_BOX_X": 255, # Used for both audio and photos
    "WINDOWS_DIALOG_SEARCH_BOX_Y": 652,
    "ADD_AUDIO_TO_TIMELINE_X": 1200,
    "ADD_AUDIO_TO_TIMELINE_Y": 219,
    "AUDIO_TRIM_POINT_X": 2039,
    "AUDIO_TRIM_POINT_Y": 1259,
    "END_ZONE_CLICK_X": 2041,
    "END_ZONE_CLICK_Y": 1153,
    "EXPORT_BUTTON_X": 2403,
    "EXPORT_BUTTON_Y": 18,
    "EXPORT_FILENAME_FIELD_X": 1453,
    "EXPORT_FILENAME_FIELD_Y": 426,
    "CONFIRM_EXPORT_BUTTON_X": 1497,
    "CONFIRM_EXPORT_BUTTON_Y": 1001,
    "CLOSE_EXPORT_SUCCESS_DIALOG_X": 1595,
    "CLOSE_EXPORT_SUCCESS_DIALOG_Y": 1001,
    "CLOSE_PROJECT_BUTTON_X": 2538,
    "CLOSE_PROJECT_BUTTON_Y": 17,
    "OPEN_SPECIFIC_TEMPLATE_BUTTON_X": 280,
    "OPEN_SPECIFIC_TEMPLATE_BUTTON_Y": 322,
    "UNDO_BUTTON_X": 84,
    "UNDO_BUTTON_Y": 791,

    # --- COORDINATES FOR OLD PHOTO REPLACEMENT METHOD (via right-click) ---
    # These coordinates are no longer used in the main photo replacement flow,
    # but are left for backward compatibility or other possible needs.
    "PHOTO_TRACK_X": 451, # General coordinate of the clip on the timeline for identification
    "PHOTO_TRACK_Y": 1037,
    "REPLACE_CLIP_MENU_ITEM_X": 569,
    "REPLACE_CLIP_MENU_ITEM_Y": 1200,
    "REPLACE_DIALOG_FILENAME_INPUT_X": 550,
    "REPLACE_DIALOG_FILENAME_INPUT_Y": 650,
    "REPLACE_DIALOG_OPEN_BUTTON_X": 1326,
    "REPLACE_DIALOG_OPEN_BUTTON_Y": 909,

    # --- NEW COORDINATES FOR PHOTO REPLACEMENT (DRAG-N-DROP as per user request) ---
    "IMPORTED_PHOTO_IN_MEDIA_POOL_X": 200, # After import, click on photo in media library (example: X=200, Y=298)
    "IMPORTED_PHOTO_IN_MEDIA_POOL_Y": 298,
    "PHOTO_TRACK_DROP_TARGET_X": 444,     # Place on timeline to drag photo to (example: X=444, Y=933)
    "PHOTO_TRACK_DROP_TARGET_Y": 933,
    "CONFIRM_REPLACE_DRAG_DROP_X": 1327,   # Button to confirm replacement after drag-n-drop (example: X=1327, Y=910)
    "CONFIRM_REPLACE_DRAG_DROP_Y": 910,
}


# --- Functions for working with coordinates ---
def save_coordinates(coords):
    try:
        with open(COORDINATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(coords, f, indent=4)
        print(f"MAIN SCRIPT: Coordinates successfully saved to {COORDINATES_FILE}")
    except Exception as e:
        print(f"MAIN SCRIPT: Error saving coordinates: {e}")

def load_coordinates():
    global coordinates
    if os.path.exists(COORDINATES_FILE):
        try:
            with open(COORDINATES_FILE, 'r', encoding='utf-8') as f:
                loaded_coords = json.load(f)
                updated_count = 0
                # default_keys = set(coordinates.keys()) # Not used
                # loaded_keys = set(loaded_coords.keys()) # Not used

                # Add new keys from code to loaded coordinates if they don't exist
                for key_default, value_default in coordinates.items():
                    if key_default not in loaded_coords:
                        loaded_coords[key_default] = value_default
                        print(f"MAIN SCRIPT: New key '{key_default}' detected in code. Added to loaded coordinates with default value: {value_default}")

                # Update current 'coordinates' with values from file
                for key, value in loaded_coords.items():
                    if key in coordinates:
                        if isinstance(value, type(coordinates.get(key, value))):
                            coordinates[key] = value
                            updated_count += 1
                        else:
                            print(f"MAIN SCRIPT: Warning: Value type for '{key}' in {COORDINATES_FILE} ({type(value)}) "
                                  f"does not match expected type ({type(coordinates.get(key, ''))}). Using default value: {coordinates.get(key, 'N/A')}")
                    else:
                        print(f"MAIN SCRIPT: Warning: Key '{key}' from {COORDINATES_FILE} is not in the current script configuration. Ignoring.")

                print(f"MAIN SCRIPT: Coordinates successfully loaded and updated ({updated_count} items) from {COORDINATES_FILE}")

                # Checks for correctness of some coordinates
                if not (isinstance(coordinates.get("EXPORT_FILENAME_FIELD_X"), int) and isinstance(coordinates.get("EXPORT_FILENAME_FIELD_Y"), int)):
                    print(f"MAIN SCRIPT: Attention! EXPORT_FILENAME_FIELD_X/Y are not numbers. Set them via the menu or leave as (0, 0).")
                    if not isinstance(coordinates.get("EXPORT_FILENAME_FIELD_X"), int): coordinates["EXPORT_FILENAME_FIELD_X"] = 0
                    if not isinstance(coordinates.get("EXPORT_FILENAME_FIELD_Y"), int): coordinates["EXPORT_FILENAME_FIELD_Y"] = 0

                # Check new critical coordinates for photo replacement
                new_photo_critical_keys_message = []
                if not (isinstance(coordinates.get("IMPORTED_PHOTO_IN_MEDIA_POOL_X"), int) and coordinates["IMPORTED_PHOTO_IN_MEDIA_POOL_X"] != 0):
                    new_photo_critical_keys_message.append("IMPORTED_PHOTO_IN_MEDIA_POOL_X")
                if not (isinstance(coordinates.get("PHOTO_TRACK_DROP_TARGET_X"), int) and coordinates["PHOTO_TRACK_DROP_TARGET_X"] != 0):
                    new_photo_critical_keys_message.append("PHOTO_TRACK_DROP_TARGET_X")

                if new_photo_critical_keys_message:
                    print(f"MAIN SCRIPT: Attention! The following coordinates for the new photo replacement method are not set (or are 0): {', '.join(new_photo_critical_keys_message)}. Photo replacement may not work correctly. Run setup (option 1).")
                elif not (isinstance(coordinates.get("PHOTO_TRACK_X"), int) and coordinates["PHOTO_TRACK_X"] != 0) : # Old check, if new ones are okay
                     print("MAIN SCRIPT: Attention! PHOTO_TRACK_X coordinate is not set (or is 0). This may affect clip identification. Setup is recommended.")

        except json.JSONDecodeError:
            print(f"MAIN SCRIPT: Error decoding JSON from {COORDINATES_FILE}. Using default coordinates (from code).")
        except Exception as e:
            print(f"MAIN SCRIPT: Error loading coordinates: {e}. Using default coordinates (from code).")
    else:
        print(f"MAIN SCRIPT: File {COORDINATES_FILE} not found. Using default coordinates (from code). You can set them up via the menu (option 1).")


# Function to capture coordinates
def get_coordinate_with_internal_listener(description_for_user):
    print("\n" + "="*50)
    print("DESCRIPTION OF THE CURRENT POINT FOR SETUP:")
    print(description_for_user)
    print("="*50)
    print("MAIN SCRIPT: Switch to the CapCut window.")
    print("MAIN SCRIPT: Move your mouse cursor over the desired element and PRESS Shift + 1 (the '!' key).")
    print("MAIN SCRIPT: Capture will stop automatically after the key press.")

    result = {"x": None, "y": None, "captured": False}

    def on_press_internal(key):
        nonlocal result
        try:
            if hasattr(key, 'char') and key.char == '!': # Using Shift + 1, which results in '!'
                x_coord, y_coord = pyautogui.position()
                result["x"] = x_coord
                result["y"] = y_coord
                result["captured"] = True
                print(f"MAIN SCRIPT (internal listener): Captured X={x_coord}, Y={y_coord}")
                return False # Stop listener
        except AttributeError:
            pass # Ignore non-character key presses (Shift, Ctrl, etc.)
        except Exception as e:
            print(f"MAIN SCRIPT (internal listener): Error in on_press_internal handler: {e}")
            return False # Stop on error

    listener_instance = None
    try:
        print("MAIN SCRIPT: Starting internal keyboard listener...")
        # Using 'with' for automatic listener resource management
        with keyboard.Listener(on_press=on_press_internal) as listener_instance:
            listener_instance.join() # Blocks until listener stops

        if result["captured"]:
            print("MAIN SCRIPT: Internal listener finished, coordinates obtained.")
            return result["x"], result["y"]
        else:
            print("MAIN SCRIPT: Internal listener finished, but coordinates were not captured (perhaps the wrong key combination was pressed).")
            return None, None
    except Exception as e:
        print(f"MAIN SCRIPT: Error with internal listener: {e}")
        if listener_instance and hasattr(listener_instance, 'stop') and listener_instance.is_alive():
            try:
                listener_instance.stop()
            except Exception as e_stop:
                 print(f"MAIN SCRIPT: Error trying to stop 'stuck' listener: {e_stop}")
        return None, None

# Interactive coordinate setup function
def setup_coordinates_interactive():
    global coordinates
    print("\n--- STARTING COORDINATE SETUP (INTERNAL MODE) ---")

    temp_coords = coordinates.copy()
    coordinate_setup_successful = True

    elements_to_setup = [
        ("TEXT_ELEMENT_ON_TIMELINE", "TEXT ON TIMELINE:\nClick on the text block on CapCut's timeline."),
        ("TEXT_BOX_IN_INSPECTOR", "TEXT INPUT FIELD:\nTop right, field for editing text."),
        ("TEXT_COLOR_PICKER_ICON", "TEXT COLOR PICKER ICON:\nIcon to open the text color palette. If you don't change color, specify any point or 0,0."),
        ("TEXT_CHOSEN_COLOR", "DESIRED COLOR IN PALETTE:\nClick on the specific color you want to use. If the previous step was 0,0, also specify 0,0 here."),
        ("EXISTING_AUDIO_TRACK", "AUDIO TRACK FOR DELETION:\nClick on an existing audio track on the timeline."),
        ("CONFIRM_DELETE_AUDIO_BUTTON", "CONFIRM AUDIO DELETION BUTTON:\nIf a 'Delete sound?' window appears, click the 'Delete'/'OK' button. If no such window, specify any screen point or 0,0."),
        ("MEDIA_TAB", "'MEDIA' TAB:\nIn the upper left part of CapCut."),
        ("IMPORT_BUTTON", "'IMPORT' BUTTON (GENERAL):\nOn the 'Media' tab. This button is used for importing both audio and photos."),
        ("WINDOWS_DIALOG_SEARCH_BOX", "'FILENAME' FIELD (DURING IMPORT):\nIn the system file selection window (when importing audio or photo), click on the filename input field."),
        ("ADD_AUDIO_TO_TIMELINE", "'+' BUTTON ON AUDIO:\nOn the imported audio in the 'Media' section, click the '+' icon to add to timeline."),
        
        # --- NEW COORDINATES FOR PHOTO REPLACEMENT (DRAG-N-DROP) ---
        ("IMPORTED_PHOTO_IN_MEDIA_POOL", "IMPORTED PHOTO IN MEDIA POOL:\nAfter importing a photo (via 'Import' -> file dialog), it will appear in CapCut's media library (usually on the left). Click on this newly imported photo. Example: X=200, Y=298."),
        ("PHOTO_TRACK_DROP_TARGET", "TARGET FOR DRAGGING PHOTO ONTO TIMELINE:\nSpecify the exact spot on the clip on the timeline WHERE the new photo will be dragged for replacement. This is the point where you 'release' the mouse. Example: X=444, Y=933."),
        ("CONFIRM_REPLACE_DRAG_DROP", "CONFIRM PHOTO REPLACEMENT (AFTER DRAGGING):\nIf a dialog appears after dragging the photo onto the timeline ('Replace clip?' etc.), click the confirmation button ('Replace', 'OK'). If no dialog, specify 0,0. Example: X=1327, Y=910."),
        
        # --- OLD PHOTO REPLACEMENT COORDINATES (FOR REFERENCE/OTHER NEEDS, NOT FOR MAIN FLOW) ---
        ("PHOTO_TRACK", "PHOTO/VIDEO CLIP ON TIMELINE (GENERAL POINT):\nClick on the photo/video clip on the timeline that will be replaced. This coordinate can be used for general clip identification, but PHOTO_TRACK_DROP_TARGET is more important for drag-n-drop."),
        # The next 3 coordinates relate to the OLD photo replacement method (via right-click) and may not be needed for the new method.
        # If you are using ONLY the new method (drag-n-drop), they can be skipped (specify 0,0).
        ("REPLACE_CLIP_MENU_ITEM", "[OLD METHOD] 'REPLACE CLIP' MENU ITEM:\n(For old method) After right-clicking on PHOTO_TRACK, specify the 'Replace clip' item in the menu. If not using, specify 0,0."),
        ("REPLACE_DIALOG_FILENAME_INPUT", "[OLD METHOD] 'FILENAME' FIELD (REPLACEMENT):\n(For old method) In the system window for replacement, the filename field. If not using, specify 0,0."),
        ("REPLACE_DIALOG_OPEN_BUTTON", "[OLD METHOD] 'OPEN' BUTTON (REPLACEMENT):\n(For old method) In the replacement window, the 'Open' button. If not using, specify 0,0."),

        ("AUDIO_TRIM_POINT", "AUDIO TRIM POINT (END OF VIDEO):\nClick on ANY clip (text, photo) on the timeline at the point where the video should end (for trimming audio)."),
        ("END_ZONE_CLICK", "'END' ZONE CLICK BEFORE EXPORT:\nSpecify a point (X=2041, Y=1153 by default) to click and press 'o' BEFORE the main 'Export' button."),
        ("EXPORT_BUTTON", "'EXPORT' BUTTON:\nMain 'Export' button in the top right corner."),
        ("EXPORT_FILENAME_FIELD", "FILENAME FIELD DURING EXPORT:\nIn the export window, click on the field for entering the filename. If you don't want to change the name automatically, specify 0,0."),
        ("CONFIRM_EXPORT_BUTTON", "'EXPORT' BUTTON (CONFIRMATION):\nButton that starts the export process in the export settings window."),
        ("CLOSE_EXPORT_SUCCESS_DIALOG", "CLOSE 'EXPORT SUCCESSFUL' DIALOG BUTTON:\n'OK'/'Done'/'Close' button in the dialog after export finishes."),
        ("CLOSE_PROJECT_BUTTON", "CLOSE PROJECT BUTTON (X):\nCross icon to close the current project (usually at the very top of the window)."),
        ("OPEN_SPECIFIC_TEMPLATE_BUTTON", "OPENING TEMPLATE:\nOn CapCut's start screen (after closing a project), click on the preview/button of your 'auto.capcut' template."),
        ("UNDO_BUTTON", "'UNDO' BUTTON:\nStandard undo action button (back arrow).")
    ]

    critical_photo_replacement_keys_new_method = [
        "IMPORTED_PHOTO_IN_MEDIA_POOL",
        "PHOTO_TRACK_DROP_TARGET"
        # CONFIRM_REPLACE_DRAG_DROP can be 0,0, so not strictly critical for *capture*
    ]

    for key_base, desc in elements_to_setup:
        x_key = key_base + "_X"
        y_key = key_base + "_Y"

        if x_key not in temp_coords or y_key not in temp_coords:
            print(f"WARNING: Keys {x_key} or {y_key} are missing from the coordinate structure. Skipping setup for '{key_base}'.")
            continue

        print(f"\n--- Setting up: {key_base.replace('_', ' ').title()} ---")
        print(f"Current values: ({temp_coords.get(x_key, 'NOT SET')}, {temp_coords.get(y_key, 'NOT SET')})")

        if key_base == "REPLACE_CLIP_MENU_ITEM": # This is for the old method, but keep instruction if someone sets it up
            print("IMPORTANT (for old method): You will now need to specify the 'Replace clip' menu item.")
            print("1. First, move your cursor over the CLIP ON THE TIMELINE (the one you specified for PHOTO_TRACK).")
            print("2. Press the RIGHT mouse button to bring up the context menu.")
            print("3. WITHOUT MOVING THE MOUSE, move the cursor over the 'Replace clip' item.")
            print("4. Press Shift + 1 ('!') when the cursor is EXACTLY on this menu item.")
            input("Press Enter when you are ready to perform these steps and press Shift+1 (or to skip if setting to 0,0)...")

        x, y = get_coordinate_with_internal_listener(desc)

        if x is not None and y is not None:
            # Handling skip for non-critical or optional coordinates
            skippable_coords_if_zero = [
                "CONFIRM_DELETE_AUDIO_BUTTON", "EXPORT_FILENAME_FIELD",
                "TEXT_COLOR_PICKER_ICON", "TEXT_CHOSEN_COLOR",
                "CONFIRM_REPLACE_DRAG_DROP",
                "REPLACE_CLIP_MENU_ITEM", "REPLACE_DIALOG_FILENAME_INPUT", "REPLACE_DIALOG_OPEN_BUTTON" # Old method
            ]
            if key_base in skippable_coords_if_zero and x == 0 and y == 0:
                print(f"MAIN SCRIPT: Skipping setup for {key_base} (set to 0,0).")
                temp_coords[x_key] = 0
                temp_coords[y_key] = 0
            else:
                temp_coords[x_key] = x
                temp_coords[y_key] = y
                print(f"MAIN SCRIPT: Coordinates for {key_base} set to: ({x}, {y})")
        else:
            print(f"MAIN SCRIPT: Failed to get coordinates for {key_base}. Current values: ({temp_coords.get(x_key, 'N/A')}, {temp_coords.get(y_key, 'N/A')})")
            if key_base in critical_photo_replacement_keys_new_method or key_base == "PHOTO_TRACK": # PHOTO_TRACK is also important
                 print(f"ERROR: Coordinates for {key_base} are CRITICAL for photo replacement. Setup aborted.")
                 coordinate_setup_successful = False
                 break
            else:
                user_choice = input("Continue setting up other coordinates (y) or abort (n)? (y/n): ").lower()
                if user_choice != 'y':
                    coordinate_setup_successful = False
                    print("MAIN SCRIPT: Coordinate setup aborted by user.")
                    break

    if coordinate_setup_successful:
        # Check if new critical photo coordinates are set
        missing_new_photo_coords = []
        for key_base_check in critical_photo_replacement_keys_new_method:
            if temp_coords.get(key_base_check + "_X") == 0 or temp_coords.get(key_base_check + "_Y") == 0:
                 missing_new_photo_coords.append(key_base_check)

        if missing_new_photo_coords:
            print("\nWARNING: The following CRITICAL coordinates for the NEW photo replacement method were not set (remained 0 or not captured):")
            for key_name in missing_new_photo_coords: print(f"- {key_name}")
            print("Photo replacement will likely NOT WORK. It is recommended to restart setup.")
            confirm_save = input("Save current (incomplete) coordinates anyway? (yes/no): ").lower()
            if confirm_save != 'yes':
                print("MAIN SCRIPT: Save cancelled. Using old coordinates.")
                return

        coordinates = temp_coords
        save_coordinates(coordinates)
        print("\n--- COORDINATE SETUP FINISHED ---")
        if not missing_new_photo_coords:
            print("MAIN SCRIPT: New values saved.")
        else:
            print("MAIN SCRIPT: Partially updated coordinates saved (with warnings above).")
    else:
        print("\n--- COORDINATE SETUP NOT FULLY COMPLETED ---")
        print("MAIN SCRIPT: Changes not saved. Using previous coordinates.")


# --- Functions for working with photos (local files) ---
def get_local_photos_list(folder_path, num_required):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print(f"Photo folder '{folder_path}' not found.")
        return []
    try:
        all_files = os.listdir(folder_path)
        # Common image extensions
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
        photo_files = [
            os.path.abspath(os.path.join(folder_path, f))
            for f in all_files
            if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(image_extensions)
        ]

        if not photo_files:
            print(f"No photo files (e.g., .jpg, .png) found in '{folder_path}'.")
            return []
        
        # Shuffle to get variety, especially if more photos than needed
        random.shuffle(photo_files) 
        
        if len(photo_files) < num_required:
            print(f"WARNING: Found {len(photo_files)} photos in '{folder_path}', but {num_required} are required for the prompts.")
            # The main loop will handle this shortage by stopping automation.
            return photo_files # Return what's found
        
        return photo_files[:num_required] # Return the required number of photos

    except Exception as e:
        print(f"Error finding photos in '{folder_path}': {e}")
        return []

# --- Helper functions ---
def get_prompts():
    prompts = {}
    if not os.path.exists(PROMPT_FILE):
        print(f"File {PROMPT_FILE} not found.")
        return prompts
    prompt_counter = 1
    try:
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            for line_content in f:
                text = line_content.strip()
                if not text: continue
                cleaned_text = re.sub(r'^\d+[\.\)]\s*', '', text).strip('"\'“”‘’ ')
                if cleaned_text:
                    prompts[prompt_counter] = cleaned_text
                    prompt_counter += 1
    except Exception as e: print(f"Error reading file {PROMPT_FILE}: {e}"); return {}
    if not prompts: print(f"No suitable lines for prompts found in file {PROMPT_FILE}.")
    return prompts

def get_used_prompts():
    used = set()
    if os.path.exists(USED_PROMPTS_FILE):
        try:
            with open(USED_PROMPTS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try: used.add(int(line.strip()))
                    except ValueError: print(f"Invalid number in {USED_PROMPTS_FILE}: {line.strip()}")
        except Exception as e: print(f"Error reading file {USED_PROMPTS_FILE}: {e}")
    return used

def mark_prompt_as_used(prompt_number):
     try:
        with open(USED_PROMPTS_FILE, 'a', encoding='utf-8') as f: f.write(str(prompt_number) + '\n')
     except Exception as e: print(f"Error writing to file {USED_PROMPTS_FILE}: {e}")

def get_random_audio_track():
    if not os.path.exists(AUDIO_FOLDER) or not os.path.isdir(AUDIO_FOLDER):
        print(f"Folder {AUDIO_FOLDER} not found."); return None
    try:
        tracks = [f for f in os.listdir(AUDIO_FOLDER) if os.path.isfile(os.path.join(AUDIO_FOLDER, f)) and f.lower().endswith(('.mp3', '.wav', '.aac'))]
        if not tracks:
            print(f"No audio files (.mp3, .wav, .aac) in folder {AUDIO_FOLDER}."); return None
        chosen_filename_with_ext = random.choice(tracks)
        filename_base, _ = os.path.splitext(chosen_filename_with_ext)
        return os.path.abspath(os.path.join(AUDIO_FOLDER, chosen_filename_with_ext)), filename_base
    except Exception as e: print(f"Error finding audio files in {AUDIO_FOLDER}: {e}"); return None

def type_text_slowly(text, interval=0.05): # Not used in current version, but might be useful
    try:
        for char in text: pyautogui.typewrite(char, interval=interval)
    except Exception as e: print(f"Error typing text: {e}")

def ensure_capcut_is_active():
    try:
        capcut_windows = pyautogui.getWindowsWithTitle("CapCut")
        if capcut_windows:
            capcut_window = capcut_windows[0]
            if not capcut_window.isActive:
                print("Activating CapCut window...")
                try:
                    capcut_window.activate()
                    time.sleep(0.5) # Give time for activation
                    if not capcut_window.isActive: # If first attempt failed
                         pyautogui.hotkey('alt', 'tab') # Try Alt+Tab
                         time.sleep(0.7)
                except Exception: # pyautogui.FailSafeException or other specific errors
                    print("Standard activation failed, trying Alt+Tab...")
                    pyautogui.hotkey('alt', 'tab')
                    time.sleep(0.7)

                # Re-check after activation attempts
                capcut_windows = pyautogui.getWindowsWithTitle("CapCut") # Refresh window list
                if capcut_windows and capcut_windows[0].isActive:
                    print("CapCut window is active.")
                    return True
                else:
                    print("WARNING: Failed to activate CapCut window. Ensure it is maximized and not obstructed.")
                    return False
            return True # Window was already active
        else:
            print("CapCut window not found. Ensure the program is running.")
            return False
    except Exception as e:
        print(f"Unexpected error during CapCut window check/activation: {e}")
        return False

def format_text_for_capcut(text, max_lines=3, target_chars_per_line_approx=25):
    words = text.split()
    if not words: return ""
    lines = []
    current_line = ""
    for word in words:
        if not current_line:
            current_line = word
        elif len(current_line) + len(word) + 1 <= target_chars_per_line_approx * 1.2: # Small buffer
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
            if len(lines) == max_lines -1: # If this is the second to last line, add everything else
                remaining_words_index = words.index(word) if word in words else -1
                if remaining_words_index != -1:
                    current_line = " ".join(words[remaining_words_index:])
                    break # Exit loop, as everything else goes into the last line
    if current_line: lines.append(current_line)

    # If more lines than max_lines, merge the last ones
    while len(lines) > max_lines:
        last_line = lines.pop()
        if lines: # Check if list is not empty
            lines[-1] += " " + last_line
        else: # If list became empty (very long word)
            lines.append(last_line)
            break # Prevent infinite loop

    return "\n".join(lines[:max_lines])


# --- Main automation logic ---
def create_video(prompt_number, prompt_text, audio_full_path, audio_filename_base, photo_full_path):
    global coordinates
    print(f"\n--- Video #{prompt_number}: {prompt_text[:40]}... ---")
    print(f"Audio: {audio_filename_base} (from '{AUDIO_FOLDER}')")
    if photo_full_path:
        print(f"Photo: {os.path.basename(photo_full_path)} (from '{AUDIO_FOLDER}')")
    else:
        print("Photo: None provided or found.") # Should not happen if main loop checks correctly

    if not ensure_capcut_is_active(): return False
    formatted_prompt_text = format_text_for_capcut(prompt_text)

    try:
        # 1. Change text
        print("1. Changing text...")
        pyautogui.click(coordinates["TEXT_ELEMENT_ON_TIMELINE_X"], coordinates["TEXT_ELEMENT_ON_TIMELINE_Y"])
        time.sleep(DELAY_UI_RESPONSE)
        pyautogui.click(coordinates["TEXT_BOX_IN_INSPECTOR_X"], coordinates["TEXT_BOX_IN_INSPECTOR_Y"], clicks=3, interval=0.1)
        time.sleep(DELAY_MINIMAL)
        pyautogui.press('delete')
        time.sleep(DELAY_MINIMAL)
        pyperclip.copy(formatted_prompt_text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(DELAY_MINIMAL)
        if coordinates["TEXT_COLOR_PICKER_ICON_X"] != 0 and coordinates["TEXT_CHOSEN_COLOR_X"] != 0:
            pyautogui.click(coordinates["TEXT_COLOR_PICKER_ICON_X"], coordinates["TEXT_COLOR_PICKER_ICON_Y"])
            time.sleep(DELAY_WINDOW_APPEAR)
            pyautogui.click(coordinates["TEXT_CHOSEN_COLOR_X"], coordinates["TEXT_CHOSEN_COLOR_Y"])
            time.sleep(DELAY_UI_RESPONSE)
            pyautogui.press('enter') # Attempt to close palette
            time.sleep(DELAY_UI_RESPONSE)
        print("Text changed.")

        # 2. Replace music
        print("2. Replacing music...")
        pyautogui.click(coordinates["EXISTING_AUDIO_TRACK_X"], coordinates["EXISTING_AUDIO_TRACK_Y"])
        time.sleep(DELAY_MINIMAL)
        pyautogui.press('delete')
        time.sleep(DELAY_UI_RESPONSE)
        if not (coordinates["CONFIRM_DELETE_AUDIO_BUTTON_X"] == 0 and coordinates["CONFIRM_DELETE_AUDIO_BUTTON_Y"] == 0):
            time.sleep(DELAY_WINDOW_APPEAR * 0.5)
            pyautogui.click(coordinates["CONFIRM_DELETE_AUDIO_BUTTON_X"], coordinates["CONFIRM_DELETE_AUDIO_BUTTON_Y"])
            time.sleep(DELAY_UI_RESPONSE)

        pyautogui.click(coordinates["MEDIA_TAB_X"], coordinates["MEDIA_TAB_Y"])
        time.sleep(DELAY_MINIMAL)
        pyautogui.click(coordinates["IMPORT_BUTTON_X"], coordinates["IMPORT_BUTTON_Y"])
        time.sleep(DELAY_WINDOW_APPEAR)
        pyautogui.click(coordinates["WINDOWS_DIALOG_SEARCH_BOX_X"], coordinates["WINDOWS_DIALOG_SEARCH_BOX_Y"])
        time.sleep(DELAY_MINIMAL * 2)
        pyautogui.hotkey('ctrl', 'a'); time.sleep(DELAY_MINIMAL); pyautogui.press('delete'); time.sleep(DELAY_MINIMAL)
        pyperclip.copy(audio_full_path)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(DELAY_UI_RESPONSE)
        pyautogui.press('enter')
        time.sleep(DELAY_PROCESSING)
        pyautogui.moveTo(coordinates["ADD_AUDIO_TO_TIMELINE_X"], coordinates["ADD_AUDIO_TO_TIMELINE_Y"])
        time.sleep(DELAY_MINIMAL)
        pyautogui.click(coordinates["ADD_AUDIO_TO_TIMELINE_X"], coordinates["ADD_AUDIO_TO_TIMELINE_Y"])
        time.sleep(DELAY_UI_RESPONSE)
        print("Music replaced.")

        # --- NEW PHOTO/VIDEO CLIP REPLACEMENT BLOCK (DRAG-N-DROP) ---
        print("3. Replacing photo/video clip (new method)...")
        if not photo_full_path:
            print("WARNING: No photo path provided, skipping photo replacement.")
        elif coordinates["IMPORT_BUTTON_X"] == 0 or \
           coordinates["WINDOWS_DIALOG_SEARCH_BOX_X"] == 0 or \
           coordinates["IMPORTED_PHOTO_IN_MEDIA_POOL_X"] == 0 or \
           coordinates["PHOTO_TRACK_DROP_TARGET_X"] == 0:
            print("ERROR: Key coordinates for new photo replacement method are not set! Skipping replacement step.")
        else:
            # Step 1: Click "Import" button (Media tab might already be active)
            pyautogui.click(coordinates["MEDIA_TAB_X"], coordinates["MEDIA_TAB_Y"]) # Ensure on correct tab
            time.sleep(DELAY_MINIMAL)
            pyautogui.click(coordinates["IMPORT_BUTTON_X"], coordinates["IMPORT_BUTTON_Y"])
            print(f"Clicked 'Import' button: ({coordinates['IMPORT_BUTTON_X']}, {coordinates['IMPORT_BUTTON_Y']})")
            time.sleep(DELAY_WINDOW_APPEAR) # Wait for file dialog

            # Step 2: Enter file name (path) in dialog
            pyautogui.click(coordinates["WINDOWS_DIALOG_SEARCH_BOX_X"], coordinates["WINDOWS_DIALOG_SEARCH_BOX_Y"])
            print(f"Clicked in dialog filename field: ({coordinates['WINDOWS_DIALOG_SEARCH_BOX_X']}, {coordinates['WINDOWS_DIALOG_SEARCH_BOX_Y']})")
            time.sleep(DELAY_MINIMAL * 2)
            pyautogui.hotkey('ctrl', 'a'); time.sleep(DELAY_MINIMAL); pyautogui.press('delete'); time.sleep(DELAY_MINIMAL)
            pyperclip.copy(photo_full_path)
            print(f"Pasting photo path: {photo_full_path}")
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(DELAY_UI_RESPONSE)
            pyautogui.press('enter') # Confirm file selection
            print("Waiting for photo import...")
            time.sleep(DELAY_PROCESSING * 1.5) # Time for photo to import into media library

            # Step 3: Select imported picture in media library
            print(f"Clicking on imported photo in media pool: ({coordinates['IMPORTED_PHOTO_IN_MEDIA_POOL_X']}, {coordinates['IMPORTED_PHOTO_IN_MEDIA_POOL_Y']})")
            pyautogui.moveTo(coordinates["IMPORTED_PHOTO_IN_MEDIA_POOL_X"], coordinates["IMPORTED_PHOTO_IN_MEDIA_POOL_Y"])
            time.sleep(DELAY_MINIMAL) # Pause before click
            pyautogui.mouseDown() # Press and hold LMB
            time.sleep(DELAY_MINIMAL) # Short pause with button held

            # Step 4: Drag to track
            print(f"Dragging photo to timeline at: ({coordinates['PHOTO_TRACK_DROP_TARGET_X']}, {coordinates['PHOTO_TRACK_DROP_TARGET_Y']})")
            pyautogui.moveTo(coordinates["PHOTO_TRACK_DROP_TARGET_X"], coordinates["PHOTO_TRACK_DROP_TARGET_Y"], duration=DRAG_DURATION)
            time.sleep(DELAY_MINIMAL) # Let mouse "settle" before release
            pyautogui.mouseUp() # Release LMB
            time.sleep(DELAY_UI_RESPONSE) # Time for UI reaction (replacement dialog appearance)

            # Step 5: Confirm replacement (if dialog exists)
            if not (coordinates["CONFIRM_REPLACE_DRAG_DROP_X"] == 0 and coordinates["CONFIRM_REPLACE_DRAG_DROP_Y"] == 0):
                print(f"Clicking to confirm replacement: ({coordinates['CONFIRM_REPLACE_DRAG_DROP_X']}, {coordinates['CONFIRM_REPLACE_DRAG_DROP_Y']})")
                pyautogui.click(coordinates["CONFIRM_REPLACE_DRAG_DROP_X"], coordinates["CONFIRM_REPLACE_DRAG_DROP_Y"])
                time.sleep(DELAY_PROCESSING) # Time for replacement processing
            else:
                print("Skipping replacement confirmation (coordinates 0,0 or not set).")
            
            print("Photo/video clip should be replaced (new method).")
        # --- END OF NEW PHOTO REPLACEMENT BLOCK ---


        # 4. Trim audio
        print("4. Trimming audio...")
        pyautogui.click(coordinates["AUDIO_TRIM_POINT_X"], coordinates["AUDIO_TRIM_POINT_Y"])
        time.sleep(DELAY_UI_RESPONSE)
        audio_track_click_y = coordinates["EXISTING_AUDIO_TRACK_Y"] + 20 # Slightly offset to hit track body
        pyautogui.click(coordinates["EXISTING_AUDIO_TRACK_X"], audio_track_click_y )
        time.sleep(DELAY_MINIMAL)
        pyautogui.press('o') # Set out point
        time.sleep(DELAY_UI_RESPONSE)
        print("Audio trimmed.")

        # 5. Export
        print("5. Exporting video...")
        if coordinates.get("END_ZONE_CLICK_X", 0) != 0 or coordinates.get("END_ZONE_CLICK_Y", 0) != 0:
            print(f"Clicking 'end coordinate' ({coordinates['END_ZONE_CLICK_X']}, {coordinates['END_ZONE_CLICK_Y']}) and pressing 'o'...")
            pyautogui.click(coordinates["END_ZONE_CLICK_X"], coordinates["END_ZONE_CLICK_Y"])
            time.sleep(DELAY_UI_RESPONSE)
            pyautogui.press('o') # This might be for setting project out point before export
            time.sleep(DELAY_UI_RESPONSE)
        pyautogui.click(coordinates["EXPORT_BUTTON_X"], coordinates["EXPORT_BUTTON_Y"])
        time.sleep(DELAY_WINDOW_APPEAR)
        output_filename_only = f"video_prompt_{prompt_number}.mp4"
        if not (coordinates["EXPORT_FILENAME_FIELD_X"] == 0 and coordinates["EXPORT_FILENAME_FIELD_Y"] == 0):
            pyautogui.click(coordinates["EXPORT_FILENAME_FIELD_X"], coordinates["EXPORT_FILENAME_FIELD_Y"], clicks=2, interval=0.1)
            time.sleep(DELAY_MINIMAL)
            pyautogui.hotkey('ctrl', 'a'); time.sleep(DELAY_MINIMAL)
            pyperclip.copy(output_filename_only)
            pyautogui.hotkey('ctrl', 'v'); time.sleep(DELAY_MINIMAL)
        pyautogui.click(coordinates["CONFIRM_EXPORT_BUTTON_X"], coordinates["CONFIRM_EXPORT_BUTTON_Y"])
        print(f"Export started. Waiting {EXPORT_WAIT_TIME} sec...")
        time.sleep(EXPORT_WAIT_TIME)
        pyautogui.click(coordinates["CLOSE_EXPORT_SUCCESS_DIALOG_X"], coordinates["CLOSE_EXPORT_SUCCESS_DIALOG_Y"])
        time.sleep(DELAY_UI_RESPONSE)
        print(f"Video #{prompt_number} created.")

        # 6. Reset project (Undo)
        print("6. Resetting project to initial state (Undo)...")
        undo_count = 25 # Number of undo operations
        for i in range(undo_count):
            pyautogui.click(coordinates["UNDO_BUTTON_X"], coordinates["UNDO_BUTTON_Y"])
            time.sleep(0.05) # Minimal delay between undos
            if (i + 1) % 5 == 0: print(f"Undo {i+1}/{undo_count}...")
        time.sleep(DELAY_UI_RESPONSE)
        print("Reset complete.")

        # 7. Close project and reopen template
        print("7. Closing current project...")
        pyautogui.click(coordinates["CLOSE_PROJECT_BUTTON_X"], coordinates["CLOSE_PROJECT_BUTTON_Y"])
        time.sleep(DELAY_WINDOW_APPEAR) # Wait for project to close and home screen to appear
        print(f"Opening template '{CAPCUT_TEMPLATE_NAME}'...")
        pyautogui.click(coordinates["OPEN_SPECIFIC_TEMPLATE_BUTTON_X"], coordinates["OPEN_SPECIFIC_TEMPLATE_BUTTON_Y"])
        print(f"Waiting for template '{CAPCUT_TEMPLATE_NAME}' to load...")
        time.sleep(DELAY_PROCESSING * 2.5) # Increased delay for template loading
        return True

    except Exception as e:
        print(f"ERROR during video creation #{prompt_number}: {e}")
        import traceback
        traceback.print_exc()
        return False

# --- Main loop ---
if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    print("Loading coordinates...")
    load_coordinates()

    while True:
        print("\n" + "="*30 + " MAIN MENU " + "="*30)
        print("1. Setup coordinates (IMPORTANT for first run and after CapCut updates!)")
        print("2. Start automation")
        print("3. Exit")
        choice = input("Select option (1-3): ")

        if choice == '1':
            print("\nATTENTION: For coordinate setup, CapCut must be RUNNING, ACTIVE, and MAXIMIZED.")
            print("Ensure your TEMPLATE project ('auto.capcut') is open.")
            confirm_setup = input("Ready to start setup? (yes/no): ").lower()
            if confirm_setup == 'yes':
                print("Switch to CapCut. Setup will begin in 5 seconds...")
                time.sleep(5)
                if not ensure_capcut_is_active():
                    print("MAIN SCRIPT: Failed to activate CapCut window. Setup cancelled.")
                    continue
                setup_coordinates_interactive()
            else:
                print("Setup cancelled.")

        elif choice == '2':
            print("Preparing for automation...")
            if not os.path.exists(AUDIO_FOLDER): os.makedirs(AUDIO_FOLDER); print(f"Created folder: {AUDIO_FOLDER} (for audio and photos)")
            if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER); print(f"Created folder: {OUTPUT_FOLDER}")

            # Check critical coordinates for NEW photo replacement method
            missing_critical_coords = []
            if coordinates.get("IMPORT_BUTTON_X", 0) == 0: missing_critical_coords.append("IMPORT_BUTTON_X/Y")
            if coordinates.get("WINDOWS_DIALOG_SEARCH_BOX_X", 0) == 0: missing_critical_coords.append("WINDOWS_DIALOG_SEARCH_BOX_X/Y")
            if coordinates.get("IMPORTED_PHOTO_IN_MEDIA_POOL_X", 0) == 0: missing_critical_coords.append("IMPORTED_PHOTO_IN_MEDIA_POOL_X/Y")
            if coordinates.get("PHOTO_TRACK_DROP_TARGET_X", 0) == 0: missing_critical_coords.append("PHOTO_TRACK_DROP_TARGET_X/Y")
            # CONFIRM_REPLACE_DRAG_DROP_X/Y can be 0,0 if no confirmation dialog, so not included in strict check here.

            if missing_critical_coords:
                 print("\nERROR: The following coordinates, necessary for the NEW photo replacement method, are not set (are 0):")
                 for coord_name in missing_critical_coords: print(f"- {coord_name}")
                 print("Please run coordinate setup (option 1).")
                 print("Automation cannot start without these coordinates.")
                 continue

            all_prompts = get_prompts()
            if not all_prompts:
                print(f"Prompts not found in {PROMPT_FILE}. Automation stopped.")
                continue
            used_prompt_numbers = get_used_prompts()
            available_prompts = {num: text for num, text in all_prompts.items() if num not in used_prompt_numbers}
            if not available_prompts:
                print(f"No NEW available prompts to process. ({PROMPT_FILE} vs {USED_PROMPTS_FILE})"); continue

            sorted_prompt_numbers = sorted(available_prompts.keys())
            num_prompts_to_process = len(sorted_prompt_numbers)
            print(f"Found {num_prompts_to_process} new prompts to process.")

            # --- NEW: Load local photos ---
            print(f"\nLoading local photos from '{AUDIO_FOLDER}'...")
            local_photo_paths = get_local_photos_list(AUDIO_FOLDER, num_prompts_to_process) 

            if not local_photo_paths or len(local_photo_paths) < num_prompts_to_process:
                print(f"\nERROR: Not enough photos found in '{AUDIO_FOLDER}'. "
                      f"Found {len(local_photo_paths) if local_photo_paths else 0} "
                      f"out of {num_prompts_to_process} required for the prompts.")
                print(f"Please add more image files (e.g., .jpg, .png) to the '{AUDIO_FOLDER}' folder.")
                print("Automation stopped.")
                continue
            
            print(f"Successfully loaded {len(local_photo_paths)} photos from '{AUDIO_FOLDER}' for the current batch.")
            # --- END NEW LOCAL PHOTOS BLOCK ---

            print("\nSTARTING AUTOMATION in 5 seconds...")
            print("MAKE SURE: 1. CAPCUT WINDOW IS ACTIVE AND MAXIMIZED. 2. TEMPLATE '{CAPCUT_TEMPLATE_NAME}' IS OPEN. 3. DO NOT TOUCH MOUSE/KEYBOARD."); time.sleep(5)

            if not ensure_capcut_is_active():
                 print("MAIN SCRIPT: Failed to activate CapCut. Automation cancelled."); continue

            processed_count, errors_count = 0, 0
            for i, prompt_num_key in enumerate(sorted_prompt_numbers):
                print(f"\n--- Processing prompt {i+1}/{num_prompts_to_process} (ID: {prompt_num_key}) ---")
                if not ensure_capcut_is_active():
                    print(f"ERROR: CapCut window not active. Automation interrupted."); errors_count += (num_prompts_to_process - i); break
                prompt_text_original = available_prompts[prompt_num_key]
                audio_data = get_random_audio_track()
                if not audio_data:
                    print(f"ERROR: No audio track for prompt ID #{prompt_num_key}. Skipping."); errors_count += 1; continue
                audio_full_path, audio_filename_base_only = audio_data
                
                # Get the photo for the current prompt
                current_photo_full_path = local_photo_paths[i] # Uses the 1:1 mapped photos

                if create_video(prompt_num_key, prompt_text_original, audio_full_path, audio_filename_base_only, current_photo_full_path):
                    mark_prompt_as_used(prompt_num_key)
                    # log_used_photo(prompt_num_key, current_photo_full_path) # REMOVED as Pexels log
                    print(f"SUCCESS: Prompt ID #{prompt_num_key} processed.")
                    processed_count += 1
                else:
                    print(f"ERROR: Failed to create video for ID #{prompt_num_key}.")
                    errors_count += 1
                    user_choice_continue = input("Continue (y) or stop (s)? (y/s): ").lower()
                    if user_choice_continue == 's':
                        print("Automation stopped by user."); errors_count += (num_prompts_to_process - (i + 1)); break # Add remaining to errors
                print("Pausing before next video..."); time.sleep(2)

            print("\n" + "="*30 + " AUTOMATION FINISHED " + "="*30)
            print(f"Successfully processed: {processed_count}")
            print(f"Errors / Skipped: {errors_count}")
            print(f"Not processed (if stopped): {num_prompts_to_process - processed_count - errors_count}")

        elif choice == '3':
            print("Exiting program."); break
        else:
            print("Invalid choice. Please select option 1, 2, or 3.")