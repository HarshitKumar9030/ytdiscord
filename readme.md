# YouTube Discord Status

This Python script integrates YouTube and YouTube Music with Discord Rich Presence, allowing you to display your currently playing YouTube video or music track as your Discord status.

## Features

- Monitors open YouTube and YouTube Music tabs in Chrome
- Fetches video information using the YouTube Data API
- Updates Discord Rich Presence with current video/music details
- Supports both YouTube and YouTube Music
- Automatically installs and configures ChromeDriver
- Handles Chrome debugging for seamless integration

## Requirements

- Python 3.6+
- Chrome browser
- Discord application
- YouTube Data API key

## Installation

1. Clone this repository or download the script.
2. Install the required Python packages:

   ```
   pip install selenium pypresence google-api-python-client chromedriver-autoinstaller psutil
   ```

3. Set up a Discord application and obtain the Client ID.
4. Set up a YouTube Data API key.

## Configuration

1. Open the script and replace the following placeholders with your actual credentials:

   ```python
   DISCORD_CLIENT_ID = "YOUR_DISCORD_CLIENT_ID"
   YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
   ```

## Usage

1. Run the script:

   ```
   python youtube_discord_status.py
   ```

2. The script will automatically connect to your Chrome browser and start monitoring YouTube and YouTube Music tabs.
3. Your Discord status will update whenever you play a video on YouTube or a track on YouTube Music.

## Notes

- Ensure that Discord is running before starting the script.
- The script uses Chrome's remote debugging feature. If you encounter any issues, try closing all Chrome windows and restarting the script.
- Your Discord status will update approximately every 15 seconds when a new video is detected.

## Troubleshooting

If you encounter any issues, check the console output for error messages. Common problems include:

- Incorrect Discord Client ID or YouTube API key
- Chrome not found or unable to connect to Chrome
- Discord not running or unable to connect to Discord

For any other issues, please open an issue on the GitHub repository.

## Author

This project was created by Harshit. You can find more of my work at [leoncyriac.me](https://leoncyriac.me).

## License

This project is open-source and available under the MIT License. See the [LICENSE](LICENSE) file for more details.