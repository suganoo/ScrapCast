import os
import requests

# GitHub Actions で環境変数がセットされていない場合のみ .env を読み込む
if "BEARER_TOKEN" not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()

BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

if not BEARER_TOKEN:
    raise EnvironmentError("BEARER_TOKEN が環境変数に設定されていません")

SEARCH_QUERY = "@ScrapCastGoGo is:quote"
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "TweetWatcher"
    return r

def search_recent_tweets():
    params = {
        "query": SEARCH_QUERY,
        "max_results": 10,
        "tweet.fields": "created_at,text,author_id,referenced_tweets",
        "expansions": "referenced_tweets.id",
        "tweet.fields": "created_at,text,author_id,referenced_tweets"
    }
    response = requests.get(SEARCH_URL, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(f"Twitter APIエラー: {response.status_code}, {response.text}")
    
    data = response.json()
    tweets = data.get("data", [])
    includes = data.get("includes", {})
    referenced_tweets = {tweet["id"]: tweet for tweet in includes.get("tweets", [])}
    
    if not tweets:
        print("新着ツイートはありません。")
    for tweet in tweets:
        process_tweet(tweet, referenced_tweets)

def process_tweet(tweet, referenced_tweets=None):
    text = tweet["text"]
    tweet_id = tweet["id"]
    tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
    
    print("========== 引用ツイート取得 ==========")
    print(f"引用ツイート本文: {text}")
    print(f"引用ツイートURL: {tweet_url}")
    
    # 引用元ツイートの情報を表示
    if tweet.get("referenced_tweets") and referenced_tweets:
        for ref in tweet["referenced_tweets"]:
            if ref["type"] == "quoted" and ref["id"] in referenced_tweets:
                quoted_tweet = referenced_tweets[ref["id"]]
                quoted_url = f"https://twitter.com/i/web/status/{ref['id']}"
                print("---------- 引用元ツイート ----------")
                print(f"引用元本文: {quoted_tweet['text']}")
                print(f"引用元URL: {quoted_url}")
    
    print("=====================================")
    # TODO: Zenn投稿、要約、Notion保存などの処理をここで呼び出す

if __name__ == "__main__":
    search_recent_tweets()
