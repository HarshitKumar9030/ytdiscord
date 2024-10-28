import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pypresence import Presence
import chromedriver_autoinstaller
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import os
import json

class YouTubeDiscordStatus:
    def __init__(self, discord_client_id, youtube_api_key):
        try:
            self.RPC = Presence(discord_client_id)
            self.RPC.connect()
            print("Connected to Discord successfully!")
            
            self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
            print("Connected to YouTube API successfully!")
            
            print("Installing ChromeDriver...")
            chromedriver_autoinstaller.install()
            
            chrome_debugging_port = self.get_chrome_debugging_port()
            
            self.chrome_options = Options()
            self.chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_debugging_port}")
            
            print("Connecting to existing Chrome browser...")
            self.driver = webdriver.Chrome(options=self.chrome_options)
            print("Connected to Chrome browser successfully!")
            
        except Exception as e:
            print(f"Initialization error: {str(e)}")
            raise

    def get_chrome_debugging_port(self):
        """Launch Chrome with remote debugging if not already running"""
        try:
            chrome_debug_port = 9222
            
            debug_port_file = "chrome_debug_port.txt"
            if os.path.exists(debug_port_file):
                with open(debug_port_file, 'r') as f:
                    chrome_debug_port = int(f.read().strip())
                print(f"Using existing Chrome debugging port: {chrome_debug_port}")
                return chrome_debug_port
            
            import subprocess
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] == 'chrome.exe' and '--remote-debugging-port' in str(proc.info['cmdline']):
                    print(f"Terminating existing Chrome debug instance: {proc.info['pid']}")
                    proc.terminate()
            
            chrome_path = self.get_chrome_path()
            if not chrome_path:
                raise Exception("Chrome installation not found!")
            
            cmd = f'"{chrome_path}" --remote-debugging-port={chrome_debug_port} --user-data-dir="%LOCALAPPDATA%\\Google\\Chrome\\User Data"'
            subprocess.Popen(cmd, shell=True)
            print(f"Started Chrome with debugging port: {chrome_debug_port}")
            
            with open(debug_port_file, 'w') as f:
                f.write(str(chrome_debug_port))
            
            time.sleep(2)  
            return chrome_debug_port
            
        except Exception as e:
            print(f"Error setting up Chrome debugging: {str(e)}")
            raise
    
    def get_chrome_path(self):
        """Get Chrome installation path"""
        possible_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def extract_video_info(self, url):
        """Extract video ID and service type from URL."""
        parsed_url = urlparse(url)
        
        # Check for YouTube Music
        if parsed_url.hostname == 'music.youtube.com':
            if parsed_url.path == '/watch':
                return {
                    'video_id': parse_qs(parsed_url.query)['v'][0],
                    'service': 'music'
                }
        # Check for regular YouTube
        elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            if parsed_url.path == '/watch':
                return {
                    'video_id': parse_qs(parsed_url.query)['v'][0],
                    'service': 'video'
                }
        return None

    def get_youtube_tabs(self):
        youtube_tabs = []
        
        try:
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                current_url = self.driver.current_url
                video_info = self.extract_video_info(current_url)
                if video_info:
                    youtube_tabs.append({
                        'handle': handle,
                        'url': current_url,
                        'video_id': video_info['video_id'],
                        'service': video_info['service']
                    })
                    print(f"Found {'YouTube Music' if video_info['service'] == 'music' else 'YouTube'} video ID: {video_info['video_id']}")
        except Exception as e:
            print(f"Error getting YouTube tabs: {str(e)}")
            
        return youtube_tabs
    
    def get_video_info(self, video_id):
        try:
            request = self.youtube.videos().list(
                part="snippet",
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                video_data = response['items'][0]['snippet']
                title = video_data['title']
                channel_name = video_data['channelTitle']
                thumbnail = video_data['thumbnails']['maxres']['url'] if 'maxres' in video_data['thumbnails'] else video_data['thumbnails']['high']['url']
                
                print(f"Found video title: {title}")
                print(f"Channel name: {channel_name}")
                return {
                    'title': title,
                    'channel': channel_name,
                    'thumbnail': thumbnail,
                    'video_id': video_id
                }
            else:
                print(f"No video data found for ID: {video_id}")
                return None
                
        except Exception as e:
            print(f"Error getting video info from YouTube API: {str(e)}")
            return None
    
    def update_discord_status(self, video_info, service_type):
        try:
            print(f"Updating Discord status with title: {video_info['title']}")
            
            if service_type == 'music':
                watch_url = f"https://music.youtube.com/watch?v={video_info['video_id']}"
                button_text = "Listen on YouTube Music"
                activity_type = "Listening to YouTube Music"
                small_image = "youtube_music"
            else:
                watch_url = f"https://youtube.com/watch?v={video_info['video_id']}"
                button_text = "Watch on YouTube"
                activity_type = "Watching YouTube"
                small_image = "youtube"
            
            self.RPC.update(
                details=video_info['title'][:128],
                state=f"by {video_info['channel']}",
                large_image=video_info['thumbnail'],
                large_text=video_info['title'],
                small_image=small_image,
                small_text=activity_type,
                start=int(time.time()),
                buttons=[
                    {"label": button_text, "url": watch_url}
                ]
            )
            print("Discord status updated successfully!")
        except Exception as e:
            print(f"Error updating Discord status: {str(e)}")
            print(f"Video info: {video_info}")
    
    def run(self):
        try:
            print("Starting YouTube/YouTube Music Discord Status Integration...")
            print("Waiting for YouTube/YouTube Music tabs...")
            last_video_id = None
            
            while True:
                youtube_tabs = self.get_youtube_tabs()
                
                if youtube_tabs:
                    current_tab = youtube_tabs[0]
                    current_video_id = current_tab['video_id']
                    
                    if current_video_id != last_video_id:
                        print(f"New {'music' if current_tab['service'] == 'music' else 'video'} detected: {current_video_id}")
                        video_info = self.get_video_info(current_video_id)
                        
                        if video_info:
                            self.update_discord_status(video_info, current_tab['service'])
                            last_video_id = current_video_id
                        else:
                            print("No valid video information found.")
                    
                time.sleep(15)
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.driver.quit()
            self.RPC.close()
            if os.path.exists("chrome_debug_port.txt"):
                os.remove("chrome_debug_port.txt")

if __name__ == "__main__":
    
    DISCORD_CLIENT_ID = ""
    
    YOUTUBE_API_KEY = ""
    print("Starting up...")
    print("Checking for existing Chrome installation...")
    
    try:
        youtube_discord = YouTubeDiscordStatus(DISCORD_CLIENT_ID, YOUTUBE_API_KEY)
        youtube_discord.run()
    except Exception as e:
        print(f"Failed to start: {str(e)}")
        input("Press Enter to exit...")