

from googleapiclient.discovery import build
import pandas as pd

# ==================================
# CONFIGURATION
# ==================================

API_KEY = "AIzaSyASThsmBsTBHzcoWFRvKiVHkcLE3pgiBPM"
CHANNEL_ID = "UC_vt34wimdCzdkrzVejwX9g"

youtube = build(
    'youtube',
    'v3',
    developerKey=API_KEY
)

# ==================================
# GET CHANNEL INFORMATION
# ==================================

channel_request = youtube.channels().list(
    part="snippet,statistics,contentDetails",
    id=CHANNEL_ID
)

channel_response = channel_request.execute()

channel_data = []

for item in channel_response["items"]:

    channel_info = {
        "Channel ID": item["id"],
        "Channel Title": item["snippet"]["title"],
        "Channel Description": item["snippet"]["description"],
        "Published At": item["snippet"]["publishedAt"],
        "Subscriber Count": item["statistics"].get("subscriberCount"),
        "View Count": item["statistics"].get("viewCount"),
        "Video Count": item["statistics"].get("videoCount")
    }

    channel_data.append(channel_info)

channel_df = pd.DataFrame(channel_data)

print(channel_df)

# ==================================
# GET UPLOAD PLAYLIST ID
# ==================================

playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# ==================================
# GET VIDEO IDS
# ==================================

video_ids = []

next_page_token = None

while True:

    playlist_request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlist_id,
        maxResults=50,
        pageToken=next_page_token
    )

    playlist_response = playlist_request.execute()

    for item in playlist_response["items"]:
        video_ids.append(
            item["contentDetails"]["videoId"]
        )

    next_page_token = playlist_response.get("nextPageToken")

    if not next_page_token:
        break

print("Total Videos:", len(video_ids))

# ==================================
# GET VIDEO DETAILS
# ==================================

video_data = []

for i in range(0, len(video_ids), 50):

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics,status",
        id=",".join(video_ids[i:i+50])
    )

    response = request.execute()

    for item in response["items"]:

        stats = item.get("statistics", {})
        status = item.get("status", {})

        video_info = {
            "Video ID": item["id"],
            "Video Title": item["snippet"]["title"],
            "Video Description": item["snippet"]["description"],
            "Published At": item["snippet"]["publishedAt"],
            "Duration": item["contentDetails"]["duration"],
            "View Count": stats.get("viewCount"),
            "Like Count": stats.get("likeCount"),
            "Comment Count": stats.get("commentCount"),
            "Privacy Status": status.get("privacyStatus")
        }

        video_data.append(video_info)

video_df = pd.DataFrame(video_data)

print(video_df.head())

# ==================================
# SAVE FILES
# ==================================

channel_df.to_csv(
    "channel_data.csv",
    index=False
)

video_df.to_csv(
    "video_data.csv",
    index=False
)

with pd.ExcelWriter(
    "youtube_data.xlsx"
) as writer:

    channel_df.to_excel(
        writer,
        sheet_name="Channel",
        index=False
    )

    video_df.to_excel(
        writer,
        sheet_name="Videos",
        index=False
    )

print("Files Saved Successfully")