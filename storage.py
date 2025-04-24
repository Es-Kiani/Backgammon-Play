
import json

def save_game_state(filename, game_state, move_history):
    data = {
        'game': game_state,
        'history': move_history
    }
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_game_state(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['game'], data.get('history', [])
