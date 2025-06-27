import os
import requests

# GitHub Actions で環境変数がセットされていない場合のみ .env を読み込む
#if "BEARER_TOKEN" not in os.environ:
#    from dotenv import load_dotenv
#    load_dotenv()

BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

if not BEARER_TOKEN:
    raise EnvironmentError("BEARER_TOKEN が環境変数に設定されていません")

SEARCH_QUERY = "@ScrapCastGoGo -is:retweet"
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "TweetWatcher"
    return r

def search_recent_tweets():
    params = {
        "query": SEARCH_QUERY,
        "max_results": 10,
        "tweet.fields": "created_at,text,author_id"
    }
    response = requests.get(SEARCH_URL, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(f"Twitter APIエラー: {response.status_code}, {response.text}")
    
    tweets = response.json().get("data", [])
    if not tweets:
        print("新着ツイートはありません。")
    for tweet in tweets:
        process_tweet(tweet)

def process_tweet(tweet):
    text = tweet["text"]
    tweet_id = tweet["id"]
    tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
    print("========== ツイート取得 ==========")
    print(f"本文: {text}")
    print(f"URL: {tweet_url}")
    # TODO: Zenn投稿、要約、Notion保存などの処理をここで呼び出す

if __name__ == "__main__":
    search_recent_tweets()
