# happyhappyhappy

[![happy-cat](./assets/happy-cat.gif)](https://www.youtube.com/watch?v=dMZ7_yTILS8)

Happy graduation to all graduates.

This project provides a command-line tool for processing videos to extract frames, crop them, and perform OCR (Optical Character Recognition) on the cropped regions. The tool outputs the extracted text along with its corresponding timestamp in the video.

## Prerequisites

Before running the tool, make sure you have the following dependencies installed:

1. **Google Tesseract OCR**

   - Installation instructions can be found [here](https://github.com/tesseract-ocr/tesseract).

2. **ffmpeg**
   - Installation instructions can be found [here](https://ffmpeg.org/download.html).

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/emptymap/happyhappyhappy.git
   cd happyhappyhappy
   ```

2. Sync rye
   ```bash
	 rye sync
	 ```

## Usage

Run the tool using the following command:

```bash
python ./src/happyhappyhappy/happy.py <video_path> --top-left <x,y> --bottom-right <x,y> [--start <seconds>] [--end <seconds>]
```

### Arguments

- `<video_path>`: Path to the video file.
- `--top-left <x,y>`: Top-left coordinates of the bounding box to crop (e.g., `100,200`).
- `--bottom-right <x,y>`: Bottom-right coordinates of the bounding box to crop (e.g., `300,400`).
- `--start <seconds>`: (Optional) Start time in seconds.
- `--end <seconds>`: (Optional) End time in seconds.

### Example

360p videos are enough for this project.
```bash
yt-dlp -f "best[height<=360]" "VIDEO_URL"
```

Top-left and bottom-right for 360p videos
```bash
rye run python ./src/happyhappyhappy/happy.py "video.mp4" --top-left "205,270" --bottom-right "640,310"
```
