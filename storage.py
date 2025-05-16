import pickle
import os

SAVE_PATH = "file_system_data.pkl"

def save_state(data):
    with open(SAVE_PATH, 'wb') as f:
        pickle.dump(data, f)

def load_state():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, 'rb') as f:
            return pickle.load(f)
    return None
