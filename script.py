import subprocess
import os
import re
import json

CHANNEL_URL = "https://www.youtube.com/channel/UC-DOmbcVPfd36RTj335YMlA/videos"

os.makedirs("transcripts", exist_ok=True)

STATE_FILE = "processed_videos.json"

# 🔹 LOAD OLD VIDEOS
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        processed = set(json.load(f))
else:
    processed = set()

print("🔍 Fetching latest 30 videos...\n")

# 🔹 FETCH VIDEOS
result = subprocess.run(
    [
        "yt-dlp",
        "--playlist-end", "30",
        "--print", "%(id)s|%(title)s",
        CHANNEL_URL
    ],
    capture_output=True,
    text=True
)

videos = []
for line in result.stdout.split("\n"):
    if "|" in line:
        vid, title = line.split("|", 1)
        videos.append((vid.strip(), title.strip()))

# 🔹 FILTER NEW
new_videos = [(vid, title) for vid, title in videos if vid not in processed]

print(f"📊 New videos found: {len(new_videos)}\n")


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


# 🔥 EXTRACT COMPANY + QUARTER
def extract_name(title):
    title = title.upper()

    # Company Name (before Q)
    company = title.split("Q")[0]

    # Clean company
    company = re.sub(r"[^A-Z0-9 ]", "", company)
    company = "_".join(company.split()).strip("_")

    # Quarter
    q_match = re.search(r"Q[1-4]", title)
    quarter = q_match.group(0) if q_match else "QX"

    # FY
    fy_match = re.search(r"FY[\d\-]+", title)
    fy = fy_match.group(0).replace("-", "") if fy_match else "FYXXXX"

    return f"{company}_{quarter}_{fy}"


# 🔹 PROCESS
for video_id, title in new_videos:
    url = f"https://youtu.be/{video_id}"
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

    vtt_files = [f for f in os.listdir() if video_id in f and f.endswith(".vtt")]

    if not vtt_files:
        print("❌ No subtitles")
        continue

    subtitle_file = vtt_files[0]
    print(f"📂 Using: {subtitle_file}")

    transcript = parse_vtt(subtitle_file)

    # 🔥 STANDARDIZED NAME
    clean_name = extract_name(title)
    save_path = f"transcripts/{clean_name}.txt"

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"✅ Saved: {save_path}")

    processed.add(video_id)


# 🔹 SAVE STATE
with open(STATE_FILE, "w") as f:
    json.dump(list(processed), f)

print("\n🔥 DONE: Clean named transcripts saved")
