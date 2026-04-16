import subprocess
import sys
import os

def parse_vtt(file_path):
    text = ""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "-->" not in line and line.strip() and not line.startswith("WEBVTT"):
                text += line.strip() + " "
    return text

def main():
    url = sys.argv[1]

    try:
        print("🔄 Downloading subtitles using yt-dlp...\n")

        subprocess.run([
            "yt-dlp",
            "--write-auto-subs",
            "--sub-lang", "en",
            "--skip-download",
            "--convert-subs", "vtt",
            url
        ], check=True)

        # find subtitle file
        for file in os.listdir():
            if file.endswith(".vtt"):
                text = parse_vtt(file)

                print("\n✅ TRANSCRIPT SUCCESS\n")
                print(text[:2000])
                return

        print("\n❌ No subtitle file found")

    except Exception as e:
        print("\n❌ FAILED")
        print(e)

if __name__ == "__main__":
    main()
