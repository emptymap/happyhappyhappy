import argparse
import tempfile
import subprocess
import glob
from PIL import Image, ImageChops
import pytesseract
from typing import Tuple, List


def parse_coordinates(coord_str: str) -> Tuple[int, int]:
    """Parses a comma-separated coordinate string into a tuple of integers."""
    return tuple(map(int, coord_str.split(",")))


def extract_frames(video_path: str, output_dir: str, fps: int = 1) -> None:
    """Extracts frames from a video at a specified frame rate."""
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            video_path,
            "-vf",
            f"fps={fps}",
            f"{output_dir}/%04d.jpg",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def list_frames(directory: str, start: int, end: int) -> List[str]:
    """Lists frame file paths in a directory, filtered by frame number range."""
    all_frames = sorted(glob.glob(f"{directory}/*.jpg"))
    return [
        frame
        for frame in all_frames
        if start <= int(frame.split("/")[-1].split(".")[0]) <= end
    ]


def crop_image(image_path: str, box: Tuple[int, int, int, int]) -> Image:
    """Crops an image to the specified bounding box."""
    image = Image.open(image_path)
    return image.crop(box)


def images_are_different(img1: Image, img2: Image, threshold: float = 30.0) -> bool:
    """Compares two images and returns True if they are different."""
    diff = ImageChops.difference(img1, img2).convert("L")
    hist = diff.histogram()
    sum_of_squares = sum(value * (idx**2) for idx, value in enumerate(hist))
    rms = (sum_of_squares / float(img1.size[0] * img1.size[1])) ** 0.5
    return rms > threshold


def process_image(image: Image) -> tuple[str, int]:
    """Processes an image to extract text using OCR."""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    text = " ".join(data["text"]).strip()
    if text == "":
        return ("", -1)
    conf = data["conf"]
    conf = [i for i in conf if i != -1]
    if len(conf) == 0:
        return ("", -1)
    min_conf = min(conf)
    return (text, min_conf)


def seconds_to_youtube_time(seconds: int) -> str:
    """Converts a given number of seconds to a YouTube-friendly time format (hh:mm:ss or mm:ss)."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02}:{minutes:02}:{secs:02}"
    else:
        return f"{minutes:02}:{secs:02}"


def main():
    parser = argparse.ArgumentParser(
        description="Process video with specified arguments"
    )
    parser.add_argument("video_path", type=str, help="Path to the video file")
    parser.add_argument(
        "--top-left", type=str, required=True, help="Top left coordinates (x,y)"
    )
    parser.add_argument(
        "--bottom-right", type=str, required=True, help="Bottom right coordinates (x,y)"
    )
    parser.add_argument(
        "--start", type=int, help="Start time in seconds", default=float("-inf")
    )
    parser.add_argument(
        "--end", type=int, help="End time in seconds", default=float("inf")
    )

    args = parser.parse_args()

    top_left = parse_coordinates(args.top_left)
    bottom_right = parse_coordinates(args.bottom_right)
    box = top_left + bottom_right

    with tempfile.TemporaryDirectory() as tmpdir:
        extract_frames(args.video_path, tmpdir)

        frames = list_frames(tmpdir, args.start, args.end)
        prev_image = None

        for frame in frames:
            current_image = crop_image(frame, box)
            if prev_image is None or images_are_different(prev_image, current_image):
                text, confidence = process_image(current_image)
                if confidence < 70:
                    continue
                seconds = int(frame.split("/")[-1].split(".")[0])
                seconds = max(0, seconds - 2)
                print(seconds_to_youtube_time(seconds), text)
            prev_image = current_image


if __name__ == "__main__":
    main()
