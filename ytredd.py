



import isodate
import sys
import praw
import re
import string
import pickledb
import schedule
from time import sleep
from requests import get
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

db_location = config['OPTIONS']['db_location']

db = pickledb.load(db_location, False)

api_key = config['YOUTUBE']['api_key']
target_channel_id = config['YOUTUBE']['target_channel_id']

client_id = config['REDDIT']['client_id']
client_secret = config['REDDIT']['client_secret']
reddit_user = config['REDDIT']['reddit_user']
reddit_pass = config['REDDIT']['reddit_pass']
user_agent = 'Youtube to Reddit (by /u/)'
target_subreddit = config['REDDIT']['target_subreddit']



max_results = config['OPTIONS']['max_results']
check_interval = config['OPTIONS']['check_interval']

reddit_on = config['NETWORKS']['reddit']


reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     username=reddit_user,
                     password=reddit_pass)





def main():
    url = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={target_channel_id}&part=snippet,id&order=date&maxResults={max_results}'
    data = get(url).json()

    for x in data['items']:
        title = x['snippet']['title']

        if x['id']['kind'] == 'youtube#playlist':
            id = x['id']['playlistId']
            playlist_url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2C+id&playlistId={id}&key={api_key}'
            playlist_data = get(playlist_url).json()
            first_id = playlist_data['items'][0]['snippet']['resourceId']['videoId']
            url = f'https://www.youtube.com/watch?v={first_id}&list={id}'







        elif x['id']['kind'] == 'youtube#video':
            id = x['id']['videoId']

            url = f'http://youtube.com/watch?v={id}'


            # #doesn't convert it from yt api duration format
            # url3 = f'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={id}&key={api_key}'
            # data1 = get(url3).json()
            # for y in data1['items']:
            #     duration = y['contentDetails']['duration']
            #     dur=isodate.parse_duration(duration)
            #     video_dur = dur.total_seconds()
            #     sys.stdout.write(duration)
            # def parsed(e):
            #     n = e.replace(/D|H|M/g,":").replace(/P|T|S/g,"").split(":")

            #     if 1==len(n):
            #         2!=len(n[0]) && (n[0]="0"+n[0]),n[0]="0:"+n[0]
            #     else:
            #         r = 1
            #         l = len(n) -1
            #         for r in l:
            #             2 != len(n[r]) && (n[r]="0"+n[r])
            #     return n.join(":")

            # import time
            # time.strftime('%Y-%m-%d', time.localtime())



        if not db.exists(id):
            for x in title:
                x = re.sub('&#39;$', '\'', x)

            if reddit_on:
                print(f'Posting {title} to Reddit')
                reddit.subreddit(target_subreddit).submit(title=title, url=url)

            db.set(id, title)
            db.dump()





schedule.every(int(check_interval)).minutes.do(main)

main()

while True:
    schedule.run_pending()
    sleep(1)
