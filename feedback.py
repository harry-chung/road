import json
import os
from datetime import datetime

FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), 'feedback.json')


def prompt_feedback(script_name: str, feedback_file: str = FEEDBACK_FILE) -> dict | None:
    """Prompt the user for feedback and save it. Returns the saved entry or None if skipped."""
    print('\n--- Feedback ---')
    rating_input = input('Rate this script (1-5), or press Enter to skip: ').strip()

    if not rating_input:
        return None

    try:
        rating = int(rating_input)
    except ValueError:
        print('Invalid rating, skipping feedback.')
        return None

    if not 1 <= rating <= 5:
        print('Rating must be between 1 and 5, skipping feedback.')
        return None

    comment = input('Any comments? (press Enter to skip): ').strip()

    entry = {
        'script': script_name,
        'rating': rating,
        'comment': comment,
        'timestamp': datetime.now().isoformat(),
    }

    _save(entry, feedback_file)
    print('Thanks for your feedback!')
    return entry


def _save(entry: dict, feedback_file: str) -> None:
    records = _load(feedback_file)
    records.append(entry)
    with open(feedback_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def _load(feedback_file: str) -> list:
    if not os.path.exists(feedback_file):
        return []
    with open(feedback_file, 'r', encoding='utf-8') as f:
        return json.load(f)
