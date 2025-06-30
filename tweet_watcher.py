import os
import requests

# --- Constants ---
LAST_TWEET_ID_VAR_NAME = "LAST_TWEET_ID"
LAST_TWEET_ID_FILENAME = "last_tweet_id.txt"
SEARCH_QUERY = "@ScrapCastGoGo is:quote"
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

# --- Environment Setup ---
# Load .env only if not in a CI environment (like GitHub Actions)
IS_CI = os.environ.get("CI")
if not IS_CI:
    from dotenv import load_dotenv
    load_dotenv()

BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")

if not BEARER_TOKEN:
    raise EnvironmentError("BEARER_TOKEN が環境変数に設定されていません")

# --- GitHub Variable Helpers ---

def _get_github_api_headers():
    if not GITHUB_TOKEN:
        # This error should only be raised in a CI environment
        raise EnvironmentError("GITHUB_TOKEN が環境変数に設定されていません")
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def _get_variable_url():
    if not GITHUB_REPOSITORY:
        # This error should only be raised in a CI environment
        raise EnvironmentError("GITHUB_REPOSITORY が環境変数に設定されていません")
    return f"https://api.github.com/repos/{GITHUB_REPOSITORY}/variables/{LAST_TWEET_ID_VAR_NAME}"

def _get_github_variable():
    """Fetches the last tweet ID from GitHub repository variables."""
    print("GitHub Actions環境を検出しました。GitHub Variableからlast_tweet_idを読み込みます。")
    try:
        response = requests.get(_get_variable_url(), headers=_get_github_api_headers())
        if response.status_code == 200:
            value = response.json().get("value")
            print(f"GitHub Variable '{LAST_TWEET_ID_VAR_NAME}' からID {value} を取得しました。")
            return value
        elif response.status_code == 404:
            print(f"GitHub Variable '{LAST_TWEET_ID_VAR_NAME}' が見つかりません。最初からツイートを検索します。")
            return None
        else:
            response.raise_for_status()
    except Exception as e:
        print(f"GitHub Variableの読み込みに失敗しました: {e}")
        return None

def _set_github_variable(tweet_id):
    """Creates or updates the last tweet ID in GitHub repository variables."""
    print(f"GitHub Variable '{LAST_TWEET_ID_VAR_NAME}' にID {tweet_id} を保存します。")
    headers = _get_github_api_headers()
    url = _get_variable_url()
    data = {"value": str(tweet_id)}

    try:
        # First, try to update the variable
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 204:
            print(f"GitHub variable '{LAST_TWEET_ID_VAR_NAME}' を更新しました。")
            return

        # If it doesn't exist (404), create it
        if response.status_code == 404:
            create_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/variables"
            create_data = {"name": LAST_TWEET_ID_VAR_NAME, "value": str(tweet_id)}
            create_response = requests.post(create_url, headers=headers, json=create_data)
            create_response.raise_for_status()
            print(f"GitHub variable '{LAST_TWEET_ID_VAR_NAME}' を作成しました。")
        else:
            response.raise_for_status()
    except Exception as e:
        print(f"GitHub Variableの更新に失敗しました: {e}")

# --- Tweet ID Persistence ---

def load_last_tweet_id():
    if IS_CI:
        return _get_github_variable()
    else:
        print("ローカル環境を検出しました。ファイルからlast_tweet_idを読み込みます。")
        try:
            with open(LAST_TWEET_ID_FILENAME, 'r') as f:
                content = f.read().strip()
                return content if content else None
        except FileNotFoundError:
            return None

def save_last_tweet_id(tweet_id):
    if IS_CI:
        _set_github_variable(tweet_id)
    else:
        print(f"ファイル '{LAST_TWEET_ID_FILENAME}' にID {tweet_id} を保存します。")
        with open(LAST_TWEET_ID_FILENAME, 'w') as f:
            f.write(str(tweet_id))

# --- Twitter API Logic ---

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "TweetWatcher"
    return r

def search_recent_tweets():
    last_tweet_id = load_last_tweet_id()
    params = {
        "query": SEARCH_QUERY,
        "max_results": 10,
        "tweet.fields": "created_at,text,author_id,referenced_tweets",
        "expansions": "referenced_tweets.id"
    }
    if last_tweet_id:
        params["since_id"] = last_tweet_id
    
    print(f"検索クエリ: {params['query']}, since_id: {last_tweet_id}")
    response = requests.get(SEARCH_URL, auth=bearer_oauth, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Twitter APIエラー: {response.status_code}, {response.text}")
    
    data = response.json()
    tweets = data.get("data", [])
    includes = data.get("includes", {})
    referenced_tweets = {tweet["id"]: tweet for tweet in includes.get("tweets", [])}
    
    if not tweets:
        print("新着ツイートはありません。")
        return
    
    newest_tweet_id = tweets[0]["id"]
    print(f"新着ツイートを {len(tweets)} 件見つけました。最新のID: {newest_tweet_id}")
    save_last_tweet_id(newest_tweet_id)
    
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
