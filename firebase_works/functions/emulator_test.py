#!/usr/bin/env python3

# Firebase Emulator用のテストスクリプト
import requests
import json
import time
from datetime import datetime, UTC

# エミュレーターの設定
FIRESTORE_EMULATOR_HOST = "127.0.0.1:8080"
FUNCTIONS_EMULATOR_HOST = "127.0.0.1:5001"

def test_http_function():
    """HTTP Cloud Functionのテスト"""
    print("🚀 HTTP Cloud Function テスト開始")
    
    endpoint = f"http://{FUNCTIONS_EMULATOR_HOST}/scrapcast-c94cc/asia-northeast1/hello_scrapcast"
    
    success = False
    try:
        print(f"🔍 試行中: {endpoint}")
        response = requests.get(endpoint, timeout=5)
        print(f"✅ HTTPレスポンス: {response.status_code}")
        print(f"📝 レスポンス内容: {response.text}")
        success = True
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    if not success:
        print("❌ 全てのエンドポイントで接続に失敗しました")
        print("🔧 エミュレーターが正しく起動しているか確認してください")

def add_test_tweet_to_firestore():
    """テスト用ツイートをFirestoreに追加"""
    print("🔥 Firestoreにテストツイートを追加")
    
    # テストツイートデータ
    test_tweet = {
        "url": "https://twitter.com/testuser/status/999888777",
        "author_username": "emulator_test_user",
        "quoted_tweet_url": "https://twitter.com/original/status/111222333",
        "text": "これはエミュレーターテスト用のツイートです 🚀✨",
        "created_at": datetime.now(UTC).isoformat(),
        "retweet_count": 15,
        "favorite_count": 42,
        "processed": False
    }
    
    try:
        # Firestore REST APIを使用してドキュメントを追加
        firestore_url = f"http://{FIRESTORE_EMULATOR_HOST}/v1/projects/scrapcast-c94cc/databases/(default)/documents/scrapcast_tweets"
        
        # Firestore形式に変換
        firestore_doc = {
            "fields": {
                "url": {"stringValue": test_tweet["url"]},
                "author_username": {"stringValue": test_tweet["author_username"]},
                "quoted_tweet_url": {"stringValue": test_tweet["quoted_tweet_url"]},
                "text": {"stringValue": test_tweet["text"]},
                "created_at": {"timestampValue": test_tweet["created_at"]},
                "retweet_count": {"integerValue": test_tweet["retweet_count"]},
                "favorite_count": {"integerValue": test_tweet["favorite_count"]},
                "processed": {"booleanValue": test_tweet["processed"]}
            }
        }
        
        response = requests.post(firestore_url, json=firestore_doc)
        
        if response.status_code == 200:
            doc_data = response.json()
            doc_id = doc_data["name"].split("/")[-1]
            print(f"✅ ツイートドキュメント追加成功: {doc_id}")
            print(f"📝 ドキュメントパス: {doc_data['name']}")
            return doc_id
        else:
            print(f"❌ ツイート追加失敗: {response.status_code}")
            print(f"📝 エラー詳細: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Firestoreテストエラー: {e}")
        return None

def check_firestore_trigger():
    """Firestoreトリガーが実行されたかチェック"""
    print("🔍 Firestoreトリガーの実行を確認中...")
    
    # しばらく待機（トリガーの実行を待つ）
    time.sleep(3)
    
    # Cloud Functionsログを確認（実際のエミュレーター環境では手動確認が必要）
    print("📋 Cloud Functionsログを確認してください:")
    print("   - process_tweet関数が実行されているか")
    print("   - ツイートデータが正しく処理されているか")
    print("   - エラーが発生していないか")

def main():
    """メインテスト関数"""
    print("🌟 Firebase Emulator テスト開始")
    print("=" * 60)
    
    # 1. HTTP Function テスト
    #test_http_function()
    print()
    
    # 2. Firestore onCreate trigger テスト
    doc_id = add_test_tweet_to_firestore()
    print()
    
    if doc_id:
        # 3. トリガー実行確認
        check_firestore_trigger()
        print()
        
        print("🎉 テスト完了！以下を確認してください:")
        print("   1. HTTP Function が正常にレスポンスを返している")
        print("   2. Firestoreにテストツイートが追加されている")
        print("   3. process_tweet関数が自動実行されている")
        print("   4. エミュレーターログにツイート処理結果が表示されている")
    else:
        print("❌ Firestoreへのデータ追加に失敗しました")
    
    print("=" * 60)
    print("✨ エミュレーターテスト終了")

if __name__ == '__main__':
    main()
