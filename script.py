import subprocess
import os
import re
import json
from datetime import datetime, timedelta

# 🔹 CHANNEL
CHANNEL_URL = "https://www.youtube.com/channel/UC-DOmbcVPfd36RTj335YMlA/videos"

# 🔹 CREATE FOLDER
os.makedirs("transcripts", exist_ok=True)

print("🔍 Fetching latest 40 videos...\n")

# 🔹 FETCH VIDEOS
result = subprocess.run(
    [
        "yt-dlp",
        "--playlist-end", "40",
        "--dump-json",
        CHANNEL_URL
    ],
    capture_output=True,
    text=True
)

# 🔹 TIME FILTER (48H SAFE)
cutoff = datetime.utcnow() - timedelta(days=2)

videos = []

for line in result.stdout.split("\n"):
    if not line.strip():
        continue

    try:
        data = json.loads(line)

        upload_date = data.get("upload_date")
        if not upload_date:
            continue

        video_time = datetime.strptime(upload_date, "%Y%m%d")

        if video_time >= cutoff:
            video_id = data["id"]
            url = f"https://youtu.be/{video_id}"
            videos.append(url)

    except:
        continue

videos = list(set(videos))

print(f"📊 Found {len(videos)} videos in last 48 hours\n")


# 🔹 CLEAN TRANSCRIPT
def parse_vtt(file_path):
    lines = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if (
                "-->" not in line
                and not line.startswith("WEBVTT")
                and not line.startswith("Kind:")
                and not line.startswith("Language:")
                and line
            ):
                line = re.sub(r"<.*?>", "", line)
                lines.append(line)

    cleaned = []
    prev = ""

    for line in lines:
        if line != prev:
            cleaned.append(line)
            prev = line

    return " ".join(cleaned)


# 🔹 PROCESS EACH VIDEO
for url in videos:
    print(f"\n🚀 Processing: {url}")

    subprocess.run([
        "yt-dlp",
        "--write-auto-subs",
        "--sub-lang", "en",
        "--skip-download",
        "--convert-subs", "vtt",
        "--output", "%(title)s [%(id)s].%(ext)s",
        url
    ])

    video_id = url.split("/")[-1]

    vtt_files = [f for f in os.listdir() if video_id in f and f.endswith(".vtt")]

    if not vtt_files:
        print("❌ No subtitles found")
        continue

    subtitle_file = vtt_files[0]
    print(f"📂 Using: {subtitle_file}")

    transcript = parse_vtt(subtitle_file)

    # 🔹 CLEAN FILE NAME
    file_name = subtitle_file.replace(".en.vtt", "").replace(" ", "_")

    save_path = f"transcripts/{file_name}.txt"

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"✅ Saved: {save_path}")

print("\n🔥 DONE: Transcripts extracted")
