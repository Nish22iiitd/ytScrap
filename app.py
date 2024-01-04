from flask import Flask,render_template
from googleapiclient.discovery import build
import csv,os,logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
app = Flask(__name__)
api_key='AIzaSyCF-ZHEq7dQ16nvNdq-SEqtDzLRCnMoB-0'
channel_id='UCphU2bAGmw304CFAzy0Enuw'
youtube=build('youtube','v3',developerKey=api_key)
# channel status
def get_channel_stats(youtube,channel_id):
    l=[]
    request=youtube.channels().list(part='snippet,contentDetails,statistics',id=channel_id)
    response=request.execute()
    data=dict(channel_name= response['items'][0]['snippet']['title'],Suscribers=response['items'][0]['statistics']['subscriberCount'],views=response['items'][0]['statistics']['viewCount'],Toatal_viedos=response['items'][0]['statistics']['videoCount'],playlist_id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
    lsut_data=l.append(data)
    return data
def get_viedo_ids(youtube,playlist_id):
    request=youtube.playlistItems().list(part='contentDetails',playlistId=playlist_id,maxResults=5)
    response=request.execute()
    viedo_ids=[]
    for i in range(len(response['items'])):
        viedo_ids.append(response['items'][i]['contentDetails']['videoId'])
    next_page_token=response.get('nextPageToken')
    more_pages=True
    while more_pages:
        if next_page_token is None: more_pages=False
        else:
            request=youtube.playlistItems().list(part='contentDetails',playlistId=playlist_id,maxResults=5,pageToken=next_page_token)
            response=request.execute()
            for i in range(len(response['items'])):
                    viedo_ids.append(response['items'][i]['contentDetails']['videoId'])
            next_page_token=response.get('nextPageToken')        
    return viedo_ids
# viedo details
def get_viedo_details(youtube,viedo_id):
    all_viedo_sts=[]
    for i in range(0,len(viedo_id),5):
        request = youtube.videos().list(part='snippet,statistics',id=','.join(viedo_id[i:i+5]))
        response=request.execute()
        for v in response['items']:
            viedo_sts=dict(Title=v['snippet']['title'],Published_date=v['snippet']['publishedAt'],Thumbnails=v['snippet']['thumbnails']['default']['url'],Views=v['statistics']['viewCount'])
            all_viedo_sts.append(viedo_sts)
    return all_viedo_sts
# storing in a csv file
def yt_srap():
    try:
        # Get channel stats
        channel_stats = get_channel_stats(youtube, channel_id)

        # Get video IDs
        video_ids = get_viedo_ids(youtube, channel_stats['playlist_id'])

        # Get video URLs
        video_urls = ["https://www.youtube.com/watch?v=" + vid for vid in video_ids]

        # Get video details
        video_details = get_viedo_details(youtube, video_ids)

        # Create a CSV file and write data
        csv_file_path = 'youtube_data.csv'

        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Video_URL', 'Title', 'Published_Date', 'Thumbnails', 'Views']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write video data to CSV
            for url, details in zip(video_urls, video_details):
                writer.writerow({
                    'Video_URL': url,
                    'Title': details['Title'],
                    'Published_Date': details['Published_date'],
                    'Thumbnails': details['Thumbnails'],
                    'Views': details['Views']
                })

        print(f'Data written to {csv_file_path}')

    except Exception as e:
        error_message = f'An error occurred: {e}'
        print(error_message)
        logging.error(error_message)
def read_csv_data():
    try:
        with open('youtube_data.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            header = next(reader, None)
            return [row for row in reader]
    except Exception as e:
        logging.error(f'An error occurred while reading CSV: {e}')
        return []

# Route to display YouTube data on a webpage
@app.route('/')
def display_youtube_data():
    try:
        data = read_csv_data()
        return render_template('youtube_data.html', data=data)
    except Exception as e:
        error_message = f'An error occurred: {e}'
        print(error_message)
        logging.error(error_message)
        return f'An error occurred: {e}'
if __name__=="__main__":
    yt_srap()
    app.run(host="0.0.0.0")
