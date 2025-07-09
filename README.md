# YouTube Audio Downloader

A powerful, feature-rich Python script for downloading YouTube videos and converting them to audio files. Built on top of yt-dlp with comprehensive rate limiting and filtering options.

## ✨ Features

- 🎵 **Audio Extraction**: Convert YouTube videos to MP3, WAV, AAC, or FLAC
- 📺 **Video Types**: Download regular videos, shorts, live streams, or all content
- 🛡️ **Rate Limiting**: Built-in protections to avoid YouTube rate limiting
- 📅 **Date Filtering**: Download videos from specific date ranges
- 🏷️ **Smart Naming**: Organized file naming with upload dates and channel names
- 📝 **Comprehensive Logging**: Detailed error logs and progress tracking
- ⚙️ **Flexible Options**: Extensive customization for different use cases

## 📋 Prerequisites

### Required Dependencies
- **Python 3.7+**
- **yt-dlp**: `pip install yt-dlp`
- **FFmpeg**: Required for audio conversion

### Installing FFmpeg

**Windows:**
1. Download from [FFmpeg official site](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🚀 Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/youtube-audio-downloader.git
cd youtube-audio-downloader
```

2. **Install dependencies:**
```bash
pip install yt-dlp
```

3. **Download audio from a channel:**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only
```

## 📖 Usage Examples

### Basic Usage

**Download all content as audio:**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only
```

**Download single video:**
```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only
```

### Content Type Filtering

**Only regular videos:**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only --video-types videos
```

**Only YouTube Shorts:**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only --video-types shorts
```

**Only live streams:**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only --video-types streams
```

### Rate Limiting (Recommended)

**Conservative settings (large channels):**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only --sleep-interval 5 --max-sleep-interval 10 --rate-limit 500K
```

**Very safe settings:**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only --sleep-interval 10 --max-sleep-interval 15 --rate-limit 300K
```

### Advanced Filtering

**Limit number of downloads:**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only --max-downloads 50
```

**Date range filtering:**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only --date-after 20240101 --date-before 20241231
```

**Minimal files (audio only, no extras):**
```bash
python youtube_downloader.py https://www.youtube.com/@channelname --audio-only --no-subs --no-metadata
```

## ⚙️ Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--audio-only` | Download audio only, skip video files | `--audio-only` |
| `--video-types` | Content type: `all`, `videos`, `shorts`, `streams` | `--video-types streams` |
| `--format` | Audio format: `mp3`, `wav`, `aac`, `flac` | `--format wav` |
| `--output` | Output directory | `--output /path/to/folder` |
| `--sleep-interval` | Sleep between downloads (seconds) | `--sleep-interval 5` |
| `--max-sleep-interval` | Maximum random sleep (seconds) | `--max-sleep-interval 10` |
| `--rate-limit` | Limit download speed | `--rate-limit 1M` |
| `--max-downloads` | Maximum number of videos | `--max-downloads 100` |
| `--date-after` | Download videos after date (YYYYMMDD) | `--date-after 20240101` |
| `--date-before` | Download videos before date (YYYYMMDD) | `--date-before 20241231` |
| `--no-subs` | Skip downloading subtitles | `--no-subs` |
| `--no-metadata` | Skip downloading metadata files | `--no-metadata` |
| `--keep-video` | Keep original video files | `--keep-video` |

## 📁 Output Structure

```
downloads/
├── audio/                          # Audio files
│   ├── ChannelName - [20240615] Video Title.mp3
│   └── ChannelName - [20240614] Another Video.mp3
├── videos/                         # Video files (if not --audio-only)
│   └── ChannelName - [20240615] Video Title.mp4
├── channel_info.json              # Channel metadata
└── error_log.txt                  # Error logs and session info
```

## 🛡️ Rate Limiting Guidelines

To avoid YouTube rate limiting, use these recommended settings:

| Channel Size | Sleep Interval | Max Sleep | Rate Limit |
|-------------|----------------|-----------|------------|
| Small (<100K subs) | 2-3 seconds | 5 seconds | 1M |
| Medium (100K-1M subs) | 3-5 seconds | 7 seconds | 500K |
| Large (1M+ subs) | 5-10 seconds | 15 seconds | 300K |

## 🎯 Use Cases

### Podcast Archival
```bash
python youtube_downloader.py https://www.youtube.com/@podcastchannel --audio-only --video-types streams --no-subs --no-metadata
```

### Educational Content
```bash
python youtube_downloader.py https://www.youtube.com/@educationchannel --audio-only --video-types videos --date-after 20240101
```

## ⚠️ Legal Considerations

- **Personal Use Only**: This tool is intended for personal, educational, and fair use purposes
- **Respect Copyright**: Only download content you have permission to download
- **Terms of Service**: Ensure compliance with YouTube's Terms of Service
- **Content Creator Rights**: Consider supporting creators through official channels

## 🐛 Troubleshooting

### Common Issues

**"ffmpeg not found" error:**
- Install FFmpeg and add it to your system PATH
- Verify installation: `ffmpeg -version`

**Rate limiting / IP blocking:**
- Increase sleep intervals: `--sleep-interval 10 --max-sleep-interval 20`
- Reduce rate limit: `--rate-limit 100K`
- Use VPN or proxy if necessary

**"Video unavailable" errors:**
- Some videos may be private, deleted, or geo-restricted
- Check the error log at `downloads/error_log.txt` for details

**Large channels timing out:**
- Use `--max-downloads` to limit the number of videos
- Use date filtering to download specific time periods

## 🙏 Acknowledgments

- Built on top of [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Uses [FFmpeg](https://ffmpeg.org/) for audio conversion

---

**Disclaimer**: This tool is for educational and personal use only. Users are responsible for complying with YouTube's Terms of Service and applicable copyright laws.
