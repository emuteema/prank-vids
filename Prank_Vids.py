from flask import Flask, render_template
from googleapiclient.discovery import build
import isodate
from datetime import datetime, timedelta

# Replace with your YouTube API key
API_KEY = 'AIzaSyDwskwwhmjV5fqVU9ObhUcOK03wO4a3Ix8'

app = Flask(__name__)

# Function to fetch prank videos
def fetch_prank_videos():
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    two_days_ago = (datetime.now() - timedelta(days=2)).isoformat("T") + "Z"

    video_ids = []
    prank_shorts = []

    # Function to fetch video details
    def fetch_video_details(video_ids):
        for i in range(0, len(video_ids), 50):  # Split into batches of 50
            video_request = youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids[i:i+50])  # Fetch in batches of 50
            )
            video_response = video_request.execute()

            for video in video_response['items']:
                if 'contentDetails' in video and 'duration' in video['contentDetails']:
                    duration = video['contentDetails']['duration']
                    duration_seconds = isodate.parse_duration(duration).total_seconds()

                    if duration_seconds < 60:  # Only Shorts
                        views = int(video['statistics'].get('viewCount', 0))
                        if views >= 100000:  # Minimum views threshold
                            prank_shorts.append({
                                'title': video['snippet']['title'],
                                'thumbnail': video['snippet']['thumbnails']['high']['url'],
                                'views': views,
                                'url': f"https://www.youtube.com/watch?v={video['id']}",
                                'published_at': video['snippet']['publishedAt']
                            })

    search_request = youtube.search().list(
        part='id',
        type='video',
        publishedAfter=two_days_ago,
        maxResults=50,
        q='prank',
        videoDuration='short'
    )

    while search_request and len(prank_shorts) < 100:
        search_response = search_request.execute()
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

        fetch_video_details(video_ids)
        search_request = youtube.search().list_next(search_request, search_response)

    return prank_shorts

# Route to display prank videos
@app.route('/')
def home():
    prank_videos = fetch_prank_videos()
    return render_template('index.html', videos=prank_videos)

if __name__ == '__main__':
    app.run(debug=True)
