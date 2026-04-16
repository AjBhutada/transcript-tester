from youtube_transcript_api import YouTubeTranscriptApi
import sys

def extract_video_id(url):
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "youtube.com" in url:
        return url.split("v=")[-1].split("&")[0]
    return None

def main():
    url = sys.argv[1]
    video_id = extract_video_id(url)

    if not video_id:
        print("❌ Invalid URL")
        return

    try:
        # NEW METHOD (FIXED)
        transcript = YouTubeTranscriptApi().fetch(video_id)

        text = " ".join([t.text for t in transcript])

        print("\n✅ TRANSCRIPT SUCCESS\n")
        print(text[:2000])

    except Exception as e:
        print("\n❌ FAILED TO FETCH TRANSCRIPT\n")
        print(e)

if __name__ == "__main__":
    main()
