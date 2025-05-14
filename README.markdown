## 📽 Demo

Click the image below to watch the demo on YouTube:

<a href="https://www.youtube.com/watch?v=AcoebqsatVw" target="_blank">
  <img src="https://img.youtube.com/vi/AcoebqsatVw/hqdefault.jpg" alt="Demo" width="480">
</a>

## Features
- **Text Replacement**: Automatically updates text in the CapCut timeline based on prompts from `promt.txt`.
- **Audio Replacement**: Randomly selects and inserts audio tracks from the `audio` folder.
- **Image Replacement**: Downloads images from Pexels API (e.g., "Luxury Cars") and replaces the video/image clip in the template using a drag-and-drop method.
- **Batch Processing**: Processes multiple prompts, tracking used prompts in `used_prompts.txt`.
- **Coordinate Setup**: Interactive setup for CapCut UI coordinates, saved in `coordinates.json`.
- **Error Handling**: Robust error handling with user prompts to continue or stop on failures.

## Prerequisites
- **Python 3.8+** installed on your system.
- **CapCut Desktop Application** installed and a template project named `auto.capcut` prepared.
- **Pexels API Key**: Obtain a free API key from [Pexels](https://www.pexels.com/api/).
- **Windows OS**: The script uses Windows-specific file dialogs and `pyautogui` for automation (macOS/Linux may require modifications).
- A monitor with consistent resolution (e.g., 1920x1080 or 2560x1440) to ensure coordinate accuracy.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/godyjooce/capcut-video-automation.git
   cd capcut-video-automation
   ```

2. **Set Up a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Pexels API Key**:
   - Open `generator.py` and replace the `PEXELS_API_KEY` value with your Pexels API key:
     ```python
     PEXELS_API_KEY = "your_pexels_api_key_here"
     ```

5. **Prepare Folders and Files**:
   - Create an `audio` folder and place `.mp3`, `.wav`, or `.aac` audio files in it.
   - Create a `promt.txt` file with one prompt per line (e.g., motivational quotes or video captions).
   - Example `promt.txt`:
     ```
     1. Success is not the absence of obstacles, but the courage to push through.
     2. Dream big, work hard, stay focused.
     3. Your only limit is your mind.
     ```

6. **Prepare CapCut Template**:
   - Create a CapCut project named `auto.capcut` with:
     - A text element on the timeline.
     - A placeholder audio track.
     - A placeholder image or video clip to be replaced.
   - Save the project and ensure it’s accessible from the CapCut start screen.

## Usage

1. **Run the Script**:
   ```bash
   python generator.py
   ```

2. **Main Menu Options**:
   - **Option 1: Setup Coordinates**:
     - Run this first to configure CapCut UI coordinates.
     - Follow on-screen instructions to click on specific UI elements (e.g., text box, import button) and press `Shift + 1` to capture coordinates.
     - Coordinates are saved in `coordinates.json`.
     - **Important**: Run this after CapCut updates or if you change your monitor resolution.
   - **Option 2: Start Automation**:
     - Processes prompts from `promt.txt`, downloading images from Pexels, and creating videos.
     - Ensure CapCut is open with the `auto.capcut` template loaded.
     - Videos are saved in the `output_videos` folder as `video_prompt_X.mp4`.
     - Used prompts are logged in `used_prompts.txt`, and used images in `used_photos_log.txt`.
   - **Option 3: Exit**: Closes the script.

3. **Automation Flow**:
   - Reads unused prompts from `promt.txt`.
   - Downloads images from Pexels (e.g., "Luxury Cars", square, large size).
   - For each prompt:
     - Updates text in the CapCut template.
     - Replaces audio with a random track from the `audio` folder.
     - Replaces the image/video clip using drag-and-drop.
     - Trims audio to match video length.
     - Exports the video.
     - Resets the project using undo and reopens the template.

4. **Important Notes**:
   - **Do not move the mouse or keyboard** during automation to avoid interrupting `pyautogui`.
   - Ensure CapCut is maximized and active before starting automation.
   - Adjust delays in `generator.py` (e.g., `DELAY_MINIMAL`, `EXPORT_WAIT_TIME`) if your system is slower or faster.
   - If automation fails, check `coordinates.json` and rerun coordinate setup (Option 1).

## File Structure
```
capcut-video-automation/
├── generator.py              # Main script
├── promt.txt                 # Input file with prompts (create manually)
├── used_prompts.txt          # Tracks used prompt IDs (auto-generated)
├── used_photos_log.txt       # Logs used Pexels images (auto-generated)
├── coordinates.json          # Stores UI coordinates (auto-generated)
├── audio/                    # Folder for audio files (create manually)
├── output_videos/            # Folder for exported videos (auto-generated)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .gitignore                # Git ignore file
```

## Requirements
See `requirements.txt` for Python dependencies. Install with:
```bash
pip install -r requirements.txt
```

## Troubleshooting
- **CapCut Not Responding**: Ensure CapCut is open, maximized, and the `auto.capcut` template is loaded. Increase delays in `generator.py` if needed.
- **Coordinate Issues**: Rerun coordinate setup (Option 1) if CapCut UI elements are misclicked.
- **Pexels API Errors**:
  - **401 Unauthorized**: Verify your Pexels API key.
  - **429 Too Many Requests**: Wait and retry later due to API rate limits.
  - **No Photos Returned**: Check the search query or try a different one (edit `download_pexels_photos` call in `generator.py`).
- **Automation Stops**: Check console output for errors. Ensure no other applications interfere with CapCut.

## Disclaimer
This script automates CapCut via GUI interactions, which can be sensitive to screen resolution, CapCut version, and system performance. Test thoroughly and adjust coordinates/delays as needed. The author is not responsible for any issues caused by automation.
