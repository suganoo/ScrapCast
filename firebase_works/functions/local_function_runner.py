#export FIRESTORE_EMULATOR_HOST="localhost:8080"
#python3 local_function_runner.py

import os
import time
import threading
from firebase_admin import credentials, firestore, initialize_app

# Important: This tells the script to look for the main.py file
# in the 'functions' subdirectory.
import sys
from main import handle_tweet_data

# --- Emulator Setup ---
# Ensure the FIRESTORE_EMULATOR_HOST environment variable is set before running.
# Example: export FIRESTORE_EMULATOR_HOST="localhost:8080"
if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
    print("Error: The FIRESTORE_EMULATOR_HOST environment variable is not set.")
    print("Please set it to your Firestore emulator's address (e.g., localhost:8080)")
    sys.exit(1)

print("Connecting to Firestore emulator...")
# When using the emulator, standard credentials are not needed.
# The SDK automatically detects the FIRESTORE_EMULATOR_HOST variable.
try:
    from firebase_admin import get_app
    get_app()
except ValueError:
    initialize_app()
db = firestore.client()

# --- Firestore Listener ---

# Create a callback function to handle changes.
# Use a threading.Event to signal when the first snapshot is received.
initial_snapshot_processed = threading.Event()

def on_snapshot(col_snapshot, changes, read_time):
    # Skip the initial data dump, only process new changes
    if not initial_snapshot_processed.is_set():
        initial_snapshot_processed.set()
        print("Initial data processed. Waiting for new documents...")
        return

    for change in changes:
        if change.type.name == 'ADDED':
            doc_id = change.document.id
            doc_data = change.document.to_dict()
            print(f"\n--- New Document Detected: {doc_id} ---")
            try:
                # Call the reusable business logic from main.py
                handle_tweet_data(db, doc_id, doc_data)
            except Exception as e:
                print(f"Error processing document {doc_id}: {e}")
            print("-----------------------------------------")

collection_ref = db.collection('scrapcast_tweets')
query_watch = collection_ref.on_snapshot(on_snapshot)

print("Firestore listener is active. Waiting for new tweet documents...")
print("(Press Ctrl+C to exit)")

# Keep the script running to listen for changes.
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping the listener...")
    query_watch.unsubscribe()
