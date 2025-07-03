/**
 * Import function triggers from their respective submodules:
 *
 * const {onCall} = require("firebase-functions/v2/https");
 * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const {setGlobalOptions} = require("firebase-functions");
const {onRequest} = require("firebase-functions/https");
const {onDocumentCreated} = require("firebase-functions/v2/firestore");
const {initializeApp} = require("firebase-admin/app");
const {getFirestore} = require("firebase-admin/firestore");
const logger = require("firebase-functions/logger");

// Initialize Firebase Admin
initializeApp();

// For cost control, you can set the maximum number of containers that can be
// running at the same time. This helps mitigate the impact of unexpected
// traffic spikes by instead downgrading performance. This limit is a
// per-function limit. You can override the limit for each function using the
// `maxInstances` option in the function's options, e.g.
// `onRequest({ maxInstances: 5 }, (req, res) => { ... })`.
// NOTE: setGlobalOptions does not apply to functions using the v1 API. V1
// functions should each use functions.runWith({ maxInstances: 10 }) instead.
// In the v1 API, each function can only serve one request per container, so
// this will be the maximum concurrent request count.
setGlobalOptions({ maxInstances: 10 });

// Create and deploy your first functions
// https://firebase.google.com/docs/functions/get-started

// ScrapCast: Firestore onCreate trigger for tweet processing
exports.processTweet = onDocumentCreated("scrapcast_tweets/{tweetId}", async (event) => {
  const snapshot = event.data;
  const tweetId = event.params.tweetId;
  
  if (!snapshot) {
    logger.error("No data associated with the event", {tweetId});
    return;
  }
  
  const tweetData = snapshot.data();
  logger.info("🔥 New tweet document created!", {
    tweetId,
    data: tweetData
  });
  
  try {
    // Get Firestore instance
    const db = getFirestore();
    
    // Display tweet processing information
    logger.info("========== ツイート処理開始 ==========");
    logger.info(`ツイートID: ${tweetId}`);
    logger.info(`引用ツイートURL: ${tweetData.url}`);
    logger.info(`投稿者: @${tweetData.author_username}`);
    logger.info(`引用元URL: ${tweetData.quoted_tweet_url || 'なし'}`);
    logger.info(`作成日時: ${tweetData.created_at}`);
    logger.info("=====================================");
    
    // Update processing status
    await snapshot.ref.update({
      'processing_status.started': true,
      'processing_status.started_at': new Date()
    });
    
    logger.info("✅ ツイート処理ステータスを更新しました");
    
    // TODO: Implement actual processing steps:
    // 1. Twitter API to get detailed tweet content
    // 2. Get user settings from scrapcast_users
    // 3. AI summarization
    // 4. GitHub repository update
    // 5. Twitter reply
    
    logger.info("🎉 ツイート処理完了（デモ版）");
    
  } catch (error) {
    logger.error("❌ ツイート処理でエラーが発生しました:", error);
    
    // Update error status
    await snapshot.ref.update({
      'processing_status.error': true,
      'processing_status.error_message': error.message,
      'processing_status.error_at': new Date()
    });
  }
});
