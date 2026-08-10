import re
import math
from typing import Dict, List, Any

# Fixed 12-word vocabulary for deterministic mock embedding
VOCABULARY = [
    "sort", "search", "binary", "insertion", "sql",
    "join", "fastapi", "pydantic", "prompt", "llm",
    "database", "validate"
]

# Exact sample notes dataset provided in task specification
SAMPLE_NOTES = [
    {"id": 1, "text": "Binary search requires a sorted array and repeatedly halves the search range using a midpoint comparison."},
    {"id": 2, "text": "Insertion sort builds a sorted list one element at a time by shifting larger elements to the right."},
    {"id": 3, "text": "FastAPI uses Pydantic models to validate request bodies and automatically generates Swagger documentation."},
    {"id": 4, "text": "SQL joins combine rows from two tables using a matching column, such as inner join, left join, and full join."},
    {"id": 5, "text": "SQL joins combine rows from two tables using a matching column, such as inner join, left join, and full join."},
    {"id": 6, "text": "Prompt engineering structures a task, context, constraints, and desired output format to guide an LLM's response."}
]


def summarize_notes(raw_text: str) -> Dict[str, Any]:
    """
    Summarizes raw study notes and produces a fixed JSON object containing:
    - topic (str)
    - key_points (List[str])
    - difficulty (str: 'easy', 'medium', or 'hard')
    
    Operates deterministically without network calls. Handles empty/whitespace input gracefully.
    """
    if not raw_text or not raw_text.strip():
        return {
            "topic": "untitled",
            "key_points": [],
            "difficulty": "easy"
        }

    clean_text = raw_text.strip()
    words = clean_text.split()
    word_count = len(words)

    # 1. Topic derivation: Clean first non-empty line or title-like prefix
    first_line = clean_text.splitlines()[0].strip()
    # Strip leading markdown symbols like # or *
    first_line = re.sub(r'^[#*-\s]+', '', first_line)
    topic = first_line[:60] if first_line else "untitled"

    # 2. Key Points derivation: Split on . / ! / ? taking up to 3 non-empty sentences
    raw_sentences = re.split(r'[.!?]+', clean_text)
    key_points = []
    for s in raw_sentences:
        stripped_sentence = s.strip()
        if stripped_sentence:
            key_points.append(stripped_sentence)
            if len(key_points) == 3:
                break

    # 3. Difficulty derivation based on word count thresholds:
    # < 40 words -> 'easy'
    # 40 - 100 words -> 'medium'
    # > 100 words -> 'hard'
    if word_count < 40:
        difficulty = "easy"
    elif word_count <= 100:
        difficulty = "medium"
    else:
        difficulty = "hard"

    return {
        "topic": topic,
        "key_points": key_points,
        "difficulty": difficulty
    }


def mock_embed(text: str) -> List[float]:
    """
    Turns any input string into a fixed-length numeric vector (12 floats) based on exact
    whole-token frequency matching against VOCABULARY.
    Tokenizes by lowercasing and splitting on non-alphanumeric characters.
    """
    if not text:
        return [0.0] * len(VOCABULARY)

    # Tokenize input string: lower-case, split by non-alphanumeric characters
    tokens = [t for t in re.split(r'[^a-zA-Z0-9]+', text.lower()) if t]

    # Count exact whole-token matches for each vocabulary word
    vector = []
    for vocab_word in VOCABULARY:
        count = sum(1 for token in tokens if token == vocab_word)
        vector.append(float(count))

    return vector


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Computes cosine similarity between two numeric vectors from first principles.
    Returns 0.0 directly if either vector is an all-zero vector (zero magnitude),
    preventing ZeroDivisionError.
    """
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(x * x for x in vec_b))

    # Zero-vector edge case guard
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    similarity = dot_product / (norm_a * norm_b)
    
    # Clamp value within [-1.0, 1.0] to account for floating point inaccuracies
    return max(-1.0, min(1.0, float(similarity)))


def search_notes_by_query(query: str) -> List[Dict[str, Any]]:
    """
    Embeds all sample notes and the search query, computes cosine similarity scores,
    and returns notes sorted by similarity score descending.
    If query embeds to an all-zero vector, returns notes with score 0.0 in original ID order.
    """
    query_vector = mock_embed(query)

    scored_notes = []
    for note in SAMPLE_NOTES:
        note_vector = mock_embed(note["text"])
        score = cosine_similarity(query_vector, note_vector)
        scored_note = {
            "id": note["id"],
            "text": note["text"],
            "score": round(score, 4)
        }
        scored_notes.append(scored_note)

    # Check if all scores are 0.0 (e.g. empty or out-of-vocabulary query)
    all_zeros = all(n["score"] == 0.0 for n in scored_notes)
    if all_zeros:
        # Keep original order by id
        return sorted(scored_notes, key=lambda x: x["id"])

    # Sort descending by score
    return sorted(scored_notes, key=lambda x: x["score"], reverse=True)
