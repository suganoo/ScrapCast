import os
import requests
import json
from datetime import datetime, timezone, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

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

# --- Firebase Setup ---
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if firebase_admin._apps:
        # Already initialized
        return firestore.client()
    
    if IS_CI:
        # GitHub Actions environment - use service account from environment variable
        print("GitHub Actions環境を検出しました。環境変数からFirebase認証情報を読み込みます。")
        service_account_key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not service_account_key:
            raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS が環境変数に設定されていません")
        
        # パス展開を明示的に行う
        expanded_path = os.path.expandvars(service_account_key)
        print(f"Firebase key path: {expanded_path}")
        print(f"Original path: {service_account_key}")
        
        # If it's a file path, use it directly
        if os.path.isfile(expanded_path):
            print("✅ ファイルが見つかりました。ファイルから認証情報を読み込みます。")
            cred = credentials.Certificate(expanded_path)
        else:
            print("⚠️ ファイルが見つかりません。JSON文字列として解析を試みます。")
            # If it's JSON content, parse it
            try:
                service_account_info = json.loads(service_account_key)
                cred = credentials.Certificate(service_account_info)
                print("✅ JSON文字列として認証情報を読み込みました。")
            except json.JSONDecodeError as e:
                raise EnvironmentError(f"Firebase認証ファイルが見つからず、JSON解析も失敗: {expanded_path}, JSON error: {e}")
    else:
        # Local development - use service account key file
        print("ローカル環境を検出しました。サービスアカウントキーファイルを読み込みます。")
        key_file = "keys/firebase-service-account-key.json"
        if not os.path.exists(key_file):
            raise EnvironmentError(f"Firebase サービスアカウントキーファイルが見つかりません: {key_file}")
        cred = credentials.Certificate(key_file)
    
    firebase_admin.initialize_app(cred)
    return firestore.client()

# --- Firestore Operations ---
def save_tweet_to_firestore(tweet, referenced_tweets, author_username):
    """Save tweet data to Firestore according to scrapcast_tweets schema"""
    try:
        db = initialize_firebase()
        
        tweet_id = tweet["id"]
        tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
        
        # Find quoted tweet URL (there should be only one)
        quoted_tweet_url = None
        if tweet.get("referenced_tweets"):
            for ref in tweet["referenced_tweets"]:
                if ref["type"] == "quoted":
                    quoted_tweet_url = f"https://twitter.com/i/web/status/{ref['id']}"
                    break
        
        # Create document data according to schema
        tweet_data = {
            "id": tweet_id,
            "url": tweet_url,
            "author_username": author_username,
            "quoted_tweet_url": quoted_tweet_url,
            "created_at": datetime.now(),
            "processed": False,
            "processing_status": {
                "summarized": False,
                "saved_to_github": False,
                "replied": False
            }
        }
        
        # Save to Firestore
        doc_ref = db.collection("scrapcast_tweets").document(tweet_id)
        doc_ref.set(tweet_data)
        
        print(f"✅ ツイート {tweet_id} をFirestoreに保存しました")
        print(f"   引用ツイートURL: {tweet_url}")
        if quoted_tweet_url:
            print(f"   引用元URL: {quoted_tweet_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Firestoreへの保存に失敗しました: {e}")
        return False

def check_tweet_exists_in_firestore(tweet_id):
    """Check if tweet already exists in Firestore to avoid duplicates"""
    try:
        db = initialize_firebase()
        doc_ref = db.collection("scrapcast_tweets").document(tweet_id)
        doc = doc_ref.get()
        
        if doc.exists:
            print(f"⚠️  ツイート {tweet_id} は既にFirestoreに存在します")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Firestore重複チェックに失敗しました: {e}")
        return False

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
    return f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/variables/{LAST_TWEET_ID_VAR_NAME}"

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
            create_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/variables"
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

def validate_tweet_id_age(tweet_id, max_age_days=7):
    """
    Tweet IDが有効期間内かチェック（7日以内）
    """
    if not tweet_id:
        return False
    
    try:
        # Twitter Snowflake IDから日時を算出
        timestamp = ((int(tweet_id) >> 22) + 1288834974657) / 1000
        tweet_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        
        is_valid = tweet_date >= cutoff_date
        
        if not is_valid:
            print(f"❌ Tweet ID {tweet_id} は古すぎます")
            print(f"   ツイート日時: {tweet_date}")
            print(f"   制限基準日時: {cutoff_date}")
        else:
            print(f"✅ Tweet ID {tweet_id} は有効です (日時: {tweet_date})")
        
        return is_valid
        
    except Exception as e:
        print(f"Tweet ID検証エラー: {e}")
        return False

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "TweetWatcher"
    return r

def search_recent_tweets():
    last_tweet_id = load_last_tweet_id()
    
    # since_idの事前検証
    if last_tweet_id and not validate_tweet_id_age(last_tweet_id):
        print("🔄 since_idが古いため、リセットして最新から検索します")
        last_tweet_id = None
    
    params = {
        "query": SEARCH_QUERY,
        "max_results": 10,
        "tweet.fields": "created_at,text,author_id,referenced_tweets",
        "expansions": "referenced_tweets.id,author_id",
        "user.fields": "username"
    }
    
    if last_tweet_id:
        params["since_id"] = last_tweet_id
        print(f"検索クエリ: {params['query']}, since_id: {last_tweet_id} (検証済み)")
    else:
        print(f"検索クエリ: {params['query']}, since_id: なし (最新から検索)")
    
    response = requests.get(SEARCH_URL, auth=bearer_oauth, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Twitter APIエラー: {response.status_code}, {response.text}")
    
    data = response.json()
    
    # デバッグ用: レスポンスデータの表示
    print("========== Twitter API レスポンス ==========")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("==========================================")
    
    tweets = data.get("data", [])
    includes = data.get("includes", {})
    referenced_tweets = {tweet["id"]: tweet for tweet in includes.get("tweets", [])}
    users = {user["id"]: user for user in includes.get("users", [])}
    
    if not tweets:
        print("新着ツイートはありません。")
        return
    
    newest_tweet_id = tweets[0]["id"]
    print(f"新着ツイートを {len(tweets)} 件見つけました。最新のID: {newest_tweet_id}")
    save_last_tweet_id(newest_tweet_id)
    
    for tweet in tweets:
        process_tweet(tweet, referenced_tweets, users)

def process_tweet(tweet, referenced_tweets=None, users=None):
    text = tweet["text"]
    tweet_id = tweet["id"]
    tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
    
    # Get author username from users data
    author_id = tweet.get("author_id")
    author_username = "unknown"
    if author_id and users and author_id in users:
        author_username = users[author_id].get("username", "unknown")
    
    print("========== 引用ツイート取得 ==========")
    print(f"引用ツイート本文: {text}")
    print(f"引用ツイートURL: {tweet_url}")
    print(f"投稿者: @{author_username}")
    
    # 引用元ツイートの情報を表示
    for ref in tweet["referenced_tweets"]:
        if ref["type"] == "quoted" and ref["id"] in referenced_tweets:
            quoted_tweet = referenced_tweets[ref["id"]]
            quoted_url = f"https://twitter.com/i/web/status/{ref['id']}"
            print("---------- 引用元ツイート ----------")
            print(f"引用元本文: {quoted_tweet['text']}")
            print(f"引用元URL: {quoted_url}")
    
    print("=====================================")
    
    # 重複チェック
    if check_tweet_exists_in_firestore(tweet_id):
        print(f"スキップ: ツイート {tweet_id} は既に処理済みです")
        return
    
    # Firestoreに保存
    success = save_tweet_to_firestore(tweet, referenced_tweets, author_username)
    
    if success:
        print(f"🎉 ツイート {tweet_id} (@{author_username}) の処理が完了しました")
    else:
        print(f"⚠️  ツイート {tweet_id} の保存に失敗しました")

if __name__ == "__main__":
    # デバッグ用: Firebase接続テスト
    print("========== Firebase接続テスト ==========")
    try:
        db = initialize_firebase()
        print("✅ Firebase接続成功")
        print(f"Firestoreクライアント: {type(db)}")
    except Exception as e:
        print(f"❌ Firebase接続失敗: {e}")
    print("=====================================")
    
    search_recent_tweets()
