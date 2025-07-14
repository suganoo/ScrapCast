# ScrapCast Cloud Functions (Python) - 2nd Gen
import os
import firebase_admin
from firebase_admin import initialize_app, firestore
from firebase_functions import https_fn, options, logger, firestore_fn
from datetime import datetime

# Global options for all functions
options.set_global_options(region=options.SupportedRegion.ASIA_NORTHEAST1)

# Initialize Firebase Admin SDK only if it hasn't been initialized.
# This is to prevent errors when this module is imported by other scripts
# that might also initialize the app (e.g., local runners).
if not firebase_admin._apps:
    logger.info("Initializing Firebase Admin SDK...")
    # Get project ID from environment variable for local development
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project_id:
        initialize_app(options={"projectId": project_id})
        logger.info(f"Firebase Admin SDK initialized with project ID: {project_id}")
    else:
        initialize_app()
        logger.info("Firebase Admin SDK initialized without explicit project ID (assuming Cloud Functions environment).")

db = firestore.client()
logger.info("Firestore db initialized.")

@https_fn.on_request()
def hello_scrapcast(req: https_fn.Request) -> https_fn.Response:
    """Simple HTTP function for testing"""
    logger.info("Hello from ScrapCast Python! (2nd Gen)")
    return https_fn.Response("Hello from ScrapCast Cloud Functions (Python)! 🐍 (2nd Gen)")

def handle_tweet_data(db: firestore.Client, tweet_id: str, tweet_data: dict) -> None:
    """
    Business logic to process a tweet.
    This is reusable and testable.
    """
    try:
        logger.info(f"🔥 Processing tweet document: {tweet_id}")
        
        logger.info("========== ツイート処理開始 ==========")
        url = tweet_data.get('url', '')
        author_username = tweet_data.get('author_username', '')
        quoted_tweet_url = tweet_data.get('quoted_tweet_url', '')
        
        logger.info(f"引用ツイートURL: {url}")
        logger.info(f"投稿者: @{author_username}")
        logger.info(f"引用元URL: {quoted_tweet_url or 'なし'}")
        logger.info("=====================================")
        
        # Update processing status
        doc_ref = db.collection('scrapcast_tweets').document(tweet_id)
        doc_ref.update({
            'processing_status.started': True,
            'processing_status.started_at': datetime.now()
        })
        
        logger.info(f"✅ ツイート処理ステータスを更新しました: {tweet_id}")
        logger.info(f"🎉 ツイート処理完了（Python版デモ）: {tweet_id}")
        
    except Exception as error:
        logger.error(f"❌ ツイート処理でエラーが発生しました: {tweet_id}, Error: {error}")
        # Error handling
        try:
            doc_ref = db.collection('scrapcast_tweets').document(tweet_id)
            doc_ref.update({
                'processing_status.error': True,
                'processing_status.error_message': str(error),
                'processing_status.error_at': datetime.now()
            })
        except Exception as e:
            logger.error(f"❌ エラーハンドリング中にさらにエラーが発生しました: {tweet_id}, Error: {e}")

#def process_tweet(event: firestore_fn.Event[firestore_fn.Change]) -> None:
@firestore_fn.on_document_created(document="scrapcast_tweets/{tweet_id}")
def process_tweet(event: firestore_fn.Event[firestore_fn.Change]) -> None:
    """
    Firestore onCreate trigger for tweet processing (2nd Gen).
    This is a thin wrapper around the business logic.
    """
    tweet_id = event.params['tweet_id']
    
    # For created documents, event.data.after contains the DocumentSnapshot
    if not event.data or not event.data.after:
        logger.warning(f"No data associated with the event for tweetId: {tweet_id}")
        return

    tweet_data = event.data.after.to_dict()
    
    handle_tweet_data(db, tweet_id, tweet_data)
