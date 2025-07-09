#!/usr/bin/env python3
"""
YouTube Video Downloader & Audio Converter
Downloads all videos from a YouTube channel and converts them to audio files.
"""

import os
import sys
import argparse
import re
from pathlib import Path
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
import json
import logging
from datetime import datetime

class YouTubeDownloader:
    def __init__(self, output_dir="downloads", audio_format="mp3", quality="best"):
        self.output_dir = Path(output_dir)
        self.audio_format = audio_format
        self.quality = quality
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "videos").mkdir(exist_ok=True)
        (self.output_dir / "audio").mkdir(exist_ok=True)
        
        # Setup error logging
        self.error_log_file = self.output_dir / "error_log.txt"
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging to file"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.error_log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Write session start
        with open(self.error_log_file, 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Session started: {datetime.now()}\n")
            f.write(f"{'='*50}\n")
    
    def log_error(self, error_msg, video_url=None):
        """Log error to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_entry = f"[{timestamp}] ERROR: {error_msg}"
        if video_url:
            error_entry += f" | URL: {video_url}"
        error_entry += "\n"
        
        with open(self.error_log_file, 'a') as f:
            f.write(error_entry)
    
    def parse_rate_limit(self, rate_limit_str):
        """Parse rate limit string and convert to bytes per second"""
        if not rate_limit_str:
            return None
        
        try:
            # Remove any whitespace and convert to uppercase
            rate_limit_str = rate_limit_str.strip().upper()
            
            # Match pattern like: 1M, 500K, 2G, etc.
            pattern = r'^(\d+(?:\.\d+)?)\s*([KMGT]?)B?$'
            match = re.match(pattern, rate_limit_str)
            if not match:
                return None
            
            number = float(match.group(1))
            unit = match.group(2)
            
            # Convert to bytes
            multipliers = {
                '': 1,
                'K': 1024,
                'M': 1024 * 1024,
                'G': 1024 * 1024 * 1024,
                'T': 1024 * 1024 * 1024 * 1024
            }
            
            return int(number * multipliers.get(unit, 1))
            
        except Exception:
            return None
    
    def download_channel_direct(self, channel_url, download_videos=True, max_workers=2, video_types='all', 
                               sleep_interval=0, max_sleep_interval=0, rate_limit=None, max_downloads=None,
                               date_after=None, date_before=None):
        """Download all videos from a channel using direct yt-dlp channel processing"""
        print(f"🔍 Processing channel directly with yt-dlp: {channel_url}")
        
        # Determine URLs to download based on video types
        urls_to_process = []
        
        # Clean base URL
        clean_url = channel_url
        if clean_url.endswith('/videos'):
            clean_url = clean_url[:-7]
        if clean_url.endswith('/live'):
            clean_url = clean_url[:-5]
        if clean_url.endswith('/streams'):
            clean_url = clean_url[:-8]
        if clean_url.endswith('/shorts'):
            clean_url = clean_url[:-7]
        
        if video_types == 'all':
            urls_to_process = [clean_url]  # Base URL gets all types
            print(f"🎯 Downloading ALL video types from: {clean_url}")
        elif video_types == 'videos':
            urls_to_process = [f"{clean_url}/videos"]
            print(f"🎯 Downloading REGULAR VIDEOS from: {clean_url}/videos")
        elif video_types == 'shorts':
            urls_to_process = [f"{clean_url}/shorts"]
            print(f"🎯 Downloading SHORTS from: {clean_url}/shorts")
        elif video_types == 'streams':
            urls_to_process = [f"{clean_url}/streams"]
            print(f"🎯 Downloading LIVE STREAMS from: {clean_url}/streams")
        
        # Common yt-dlp options with rate limiting
        base_opts = {
            'extract_flat': False,  # We want full video info
            'writeinfojson': not getattr(self, 'no_metadata', False),
            'writesubtitles': not getattr(self, 'no_subs', False),
            'writeautomaticsub': not getattr(self, 'no_subs', False),
            'subtitleslangs': ['en'] if not getattr(self, 'no_subs', False) else [],
            'ignoreerrors': True,  # Continue on errors
            'no_warnings': False,
            'playlistend': max_downloads,  # Limit number of downloads
            'keepvideo': getattr(self, 'keep_video', False),
            'no_color': True,
            'continue_dl': True,
            'retries': 3,
        }
        
        # Add rate limiting options
        if sleep_interval > 0:
            base_opts['sleep_interval'] = sleep_interval
            print(f"⏱️  Sleep interval: {sleep_interval} seconds between downloads")
        
        if max_sleep_interval > 0:
            base_opts['max_sleep_interval'] = max_sleep_interval
            print(f"⏱️  Random sleep: 0-{max_sleep_interval} seconds between downloads")
        
        if rate_limit:
            # Convert rate limit to bytes per second to avoid string comparison issues
            rate_limit_bytes = self.parse_rate_limit(rate_limit)
            if rate_limit_bytes:
                base_opts['ratelimit'] = rate_limit_bytes
                print(f"🐌 Rate limit: {rate_limit} ({rate_limit_bytes} bytes/sec)")
            else:
                print(f"⚠️  Invalid rate limit format: {rate_limit}")
        
        # Add date filtering
        if date_after:
            base_opts['dateafter'] = date_after
            print(f"📅 Only downloading videos after: {date_after}")
        
        if date_before:
            base_opts['datebefore'] = date_before
            print(f"📅 Only downloading videos before: {date_before}")
        
        if max_downloads:
            print(f"🔢 Maximum downloads: {max_downloads}")
        
        successful = 0
        failed = 0
        total_downloaded = 0
        
        try:
            # Process each URL type
            for url in urls_to_process:
                print(f"\n🚀 Processing: {url}")
                
                if download_videos:
                    # Download videos
                    video_opts = base_opts.copy()
                    video_opts.update({
                        'format': self.quality,
                        'outtmpl': str(self.output_dir / 'videos' / '%(uploader)s - [%(upload_date)s] %(title)s.%(ext)s'),
                    })
                    
                    print(f"📹 Downloading videos...")
                    with yt_dlp.YoutubeDL(video_opts) as ydl:
                        try:
                            ydl.download([url])
                            print(f"✅ Video downloads completed for {url}")
                        except Exception as e:
                            error_msg = f"Error downloading videos from {url}: {e}"
                            print(f"❌ {error_msg}")
                            self.log_error(error_msg, url)
                
                # Download and convert to audio
                audio_opts = base_opts.copy()
                audio_opts.update({
                    'format': 'bestaudio/best',
                    'outtmpl': str(self.output_dir / 'audio' / '%(uploader)s - [%(upload_date)s] %(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.audio_format,
                        'preferredquality': '192',
                    }],
                })
                
                print(f"🎵 Extracting audio from: {url}")
                
                class ProgressHook:
                    def __init__(self, parent, url_label):
                        self.parent = parent
                        self.successful = 0
                        self.failed = 0
                        self.url_label = url_label
                    
                    def __call__(self, d):
                        try:
                            if d['status'] == 'finished':
                                self.successful += 1
                                filename = d.get('filename', 'Unknown')
                                # Extract just the filename from the path
                                if filename != 'Unknown':
                                    filename = filename.split('\\')[-1].split('/')[-1]
                                print(f"✅ Audio extracted: {filename}")
                                print(f"📈 Progress ({self.url_label}): Success: {self.successful}, Failed: {self.failed}")
                            elif d['status'] == 'error':
                                self.failed += 1
                                error_msg = f"Failed to extract audio: {d.get('filename', 'Unknown')}"
                                print(f"❌ {error_msg}")
                                self.parent.log_error(error_msg)
                                print(f"📈 Progress ({self.url_label}): Success: {self.successful}, Failed: {self.failed}")
                        except Exception as e:
                            # Ignore hook errors to prevent crashes
                            pass
                
                progress_hook = ProgressHook(self, url.split('/')[-1] or 'all')
                audio_opts['progress_hooks'] = [progress_hook]
                
                with yt_dlp.YoutubeDL(audio_opts) as ydl:
                    try:
                        ydl.download([url])
                        successful += progress_hook.successful
                        failed += progress_hook.failed
                        print(f"✅ Audio extraction completed for {url}")
                    except Exception as e:
                        error_msg = f"Error during audio extraction from {url}: {e}"
                        print(f"❌ {error_msg}")
                        self.log_error(error_msg, url)
                        failed += 1
            
            # Get channel info for summary
            try:
                info_opts = {
                    'extract_flat': True,
                    'quiet': True,
                }
                with yt_dlp.YoutubeDL(info_opts) as ydl:
                    for url in urls_to_process:
                        try:
                            channel_info = ydl.extract_info(url, download=False)
                            if channel_info and 'entries' in channel_info:
                                total_downloaded += len([e for e in channel_info['entries'] if e])
                        except:
                            pass  # Skip if can't get info
                    
                    # Save channel info for the main URL
                    if urls_to_process:
                        main_info = ydl.extract_info(urls_to_process[0], download=False)
                        with open(self.output_dir / 'channel_info.json', 'w') as f:
                            json.dump(main_info, f, indent=2)
                            
            except Exception as e:
                self.log_error(f"Could not extract channel info: {e}")
        
        except Exception as e:
            error_msg = f"Critical error during channel download: {e}"
            print(f"❌ {error_msg}")
            self.log_error(error_msg, str(urls_to_process))
        
        print(f"\n🏁 Download complete!")
        print(f"✅ Successfully processed: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total videos found: {total_downloaded}")
        print(f"📁 Files saved to: {self.output_dir.absolute()}")
        print(f"📋 Error log saved to: {self.error_log_file.absolute()}")
        
        # Write summary to error log
        with open(self.error_log_file, 'a') as f:
            f.write(f"\nSession Summary:\n")
            f.write(f"URLs processed: {urls_to_process}\n")
            f.write(f"Video types: {video_types}\n")
            f.write(f"Total videos found: {total_downloaded}\n")
            f.write(f"Successfully processed: {successful}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Rate limiting: sleep={sleep_interval}s, max_sleep={max_sleep_interval}s, rate_limit={rate_limit}\n")
            f.write(f"Session ended: {datetime.now()}\n")
    
    def download_video(self, video_url, download_video=True):
        """Download a single video and convert to audio"""
        video_title = "Unknown"
        
        try:
            # Check if the video is available
            check_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(check_opts) as ydl:
                try:
                    info = ydl.extract_info(video_url, download=False)
                    video_title = info.get('title', 'Unknown')
                    
                    if not info:
                        error_msg = f"Video not available: {video_title}"
                        print(f"❌ {error_msg}")
                        self.log_error(error_msg, video_url)
                        return False
                        
                except Exception as e:
                    error_msg = f"Error checking video availability: {e}"
                    print(f"❌ {error_msg}")
                    self.log_error(error_msg, video_url)
                    return False
            
            # Common options
            base_opts = {
                'format': self.quality,
                'outtmpl': str(self.output_dir / 'videos' / '%(title)s.%(ext)s'),
                'writeinfojson': not getattr(self, 'no_metadata', False),
                'writesubtitles': not getattr(self, 'no_subs', False),
                'writeautomaticsub': not getattr(self, 'no_subs', False),
                'subtitleslangs': ['en'] if not getattr(self, 'no_subs', False) else [],
                'ignoreerrors': False,
                'no_warnings': True,
                'keepvideo': getattr(self, 'keep_video', False),
            }
            
            # Download video if requested
            if download_video:
                print(f"📹 Downloading video: {video_title}")
                try:
                    with yt_dlp.YoutubeDL(base_opts) as ydl:
                        ydl.download([video_url])
                except Exception as e:
                    error_msg = f"Failed to download video '{video_title}': {e}"
                    print(f"❌ {error_msg}")
                    self.log_error(error_msg, video_url)
                    # Continue to try audio extraction
            
            # Download and convert to audio
            audio_opts = base_opts.copy()
            audio_opts.update({
                'format': 'bestaudio/best',
                'outtmpl': str(self.output_dir / 'audio' / '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.audio_format,
                    'preferredquality': '192',
                }],
            })
            
            print(f"🎵 Extracting audio: {video_title}")
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([video_url])
            
            print(f"✅ Successfully processed: {video_title}")
            return True
            
        except Exception as e:
            error_msg = f"Error processing '{video_title}': {e}"
            print(f"❌ {error_msg}")
            self.log_error(error_msg, video_url)
            return False

def main():
    parser = argparse.ArgumentParser(description='Download YouTube videos and convert to audio')
    parser.add_argument('url', help='YouTube channel URL or video URL')
    parser.add_argument('-o', '--output', default='downloads', help='Output directory (default: downloads)')
    parser.add_argument('-f', '--format', default='mp3', choices=['mp3', 'wav', 'aac', 'flac'], 
                       help='Audio format (default: mp3)')
    parser.add_argument('-q', '--quality', default='best', help='Video quality (default: best)')
    parser.add_argument('--audio-only', action='store_true', help='Download audio only, skip video files')
    parser.add_argument('--workers', type=int, default=2, help='Number of parallel downloads (default: 2, unused for channels)')
    parser.add_argument('--no-subs', action='store_true', help='Skip downloading subtitles')
    parser.add_argument('--no-metadata', action='store_true', help='Skip downloading metadata (.info.json files)')
    parser.add_argument('--keep-video', action='store_true', help='Keep original video files after audio extraction')
    parser.add_argument('--sleep-interval', type=int, default=0, help='Sleep between downloads (seconds, 0=no sleep)')
    parser.add_argument('--max-sleep-interval', type=int, default=0, help='Maximum random sleep (seconds, 0=no random sleep)')
    parser.add_argument('--video-types', choices=['all', 'videos', 'shorts', 'streams'], default='all', 
                       help='Which video types to download: all, videos, shorts, streams (default: all)')
    parser.add_argument('--rate-limit', type=str, help='Limit download speed (e.g., 50K, 1M)')
    parser.add_argument('--max-downloads', type=int, help='Maximum number of videos to download')
    parser.add_argument('--date-after', type=str, help='Download videos after this date (YYYYMMDD)')
    parser.add_argument('--date-before', type=str, help='Download videos before this date (YYYYMMDD)')
    
    args = parser.parse_args()
    
    # Check if ffmpeg is available
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, text=True)
        print("✅ ffmpeg is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Warning: ffmpeg not found. Audio conversion may not work.")
        print("📥 Install ffmpeg: https://ffmpeg.org/download.html")
        return
    
    # Validate URL
    if not ('youtube.com' in args.url or 'youtu.be' in args.url):
        print("❌ Please provide a valid YouTube URL")
        return
    
    downloader = YouTubeDownloader(
        output_dir=args.output,
        audio_format=args.format,
        quality=args.quality
    )
    
    # Set options based on arguments
    downloader.no_subs = args.no_subs
    downloader.no_metadata = args.no_metadata
    downloader.keep_video = args.keep_video
    
    # Detect if it's a channel or single video
    if any(x in args.url for x in ['channel', 'user', '/c/', '/@']):
        # Use direct channel processing - let yt-dlp handle the channel
        downloader.download_channel_direct(
            args.url, 
            not args.audio_only, 
            args.workers,
            args.video_types,
            args.sleep_interval,
            args.max_sleep_interval,
            args.rate_limit,
            args.max_downloads,
            args.date_after,
            args.date_before
        )
    else:
        # Single video
        print("📹 Downloading single video...")
        success = downloader.download_video(args.url, not args.audio_only)
        if success:
            print("✅ Download completed successfully!")
        else:
            print("❌ Download failed!")

if __name__ == "__main__":
    main()
