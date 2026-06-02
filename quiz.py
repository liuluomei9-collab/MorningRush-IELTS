"""Quiz logic: weighted word selection and multiple-choice generation."""

import random
from datetime import date
from db import load_words, get_progress, init_db

WORDS_PER_DAY = 20


def select_words(n=WORDS_PER_DAY):
    words = load_words()
    scored = []
    today = date.today().isoformat()
    for w in words:
        p = get_progress(w["word"])
        weight = 1.0
        if p["mastered"]:
            weight *= 0.1
        if p["last_seen"] == today:
            weight *= 0.3
        if p["wrong_count"] > p["correct_count"]:
            weight *= 3.0
        elif p["correct_count"] == 0 and p["wrong_count"] == 0:
            weight *= 2.0
        scored.append((w, weight))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:n * 3]
    chosen = random.sample(top, min(n, len(top)))
    return [item[0] for item in chosen]


def generate_options(word_entry, all_words=None):
    if all_words is None:
        all_words = load_words()
    correct = word_entry["meaning"]
    pool = [w["meaning"] for w in all_words if w["meaning"] != correct]
    random.shuffle(pool)
    distractors = pool[:3]
    options = [correct] + distractors
    random.shuffle(options)
    return options


class QuizSession:
    def __init__(self, words_per_day=WORDS_PER_DAY, words=None):
        init_db()
        if words:
            self.words = words
        else:
            self.words = select_words(words_per_day)
        self.index = 0
        self.correct = 0
        self.all_words = load_words()
        self.is_review = words is not None

    @property
    def current(self):
        if self.index < len(self.words):
            return self.words[self.index]

    @property
    def total(self):
        return len(self.words)

    @property
    def is_done(self):
        return self.index >= len(self.words)

    def get_options(self):
        if self.current:
            return generate_options(self.current, self.all_words)

    def answer(self, chosen_meaning):
        if self.is_done:
            return None
        word = self.current
        correct = word["meaning"]
        is_correct = (chosen_meaning == correct)
        if is_correct:
            self.correct += 1
        from db import record_answer, update_daily_log
        record_answer(word["word"], is_correct)
        update_daily_log(is_correct)
        self.index += 1
        return is_correct, correct