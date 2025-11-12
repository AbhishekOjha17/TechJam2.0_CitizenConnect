# pipeline/nlp_cleaning.py

import re
import emoji
import ftfy
from better_profanity import profanity
import spacy

# ✅ Load NLP resources once at module load
nlp = spacy.load("en_core_web_sm")
print("✅ spaCy model loaded successfully")

profanity.load_censor_words()
print("✅ Profanity filter initialized")


def conservative_clean(comment: str) -> str | None:
    """
    Perform minimal but safe NLP-based cleaning.
    Keeps meaning intact and avoids over-cleaning.
    """

    if not comment or not comment.strip():
        return None

    # --- Step 1: Basic normalization ---
    original = comment.strip()
    text = ftfy.fix_text(original)                      # Fix text encoding
    text = emoji.replace_emoji(text, replace=" ")        # Remove emojis
    text = re.sub(r"http\S+|www\S+", "[URL]", text)      # Replace URLs
    text = text.replace("\n", " ").replace("\r", " ")    # Remove newlines
    text = re.sub(r"\s+", " ", text).strip()             # Clean extra spaces

    if not text:
        return original

    # --- Step 2: spaCy token-level cleaning ---
    doc = nlp(text)
    tokens = []

    for token in doc:
        tok = token.text

        if token.is_space:
            continue
        if token.is_punct:
            tokens.append(tok)
            continue
        if token.is_alpha or token.like_num or token.like_url:
            tokens.append(tok)
            continue
        if tok.strip():
            tokens.append(tok)

    cleaned = " ".join(tokens).strip()

    # --- Step 3: Add named entities (helps with context retention) ---
    for ent in doc.ents:
        if ent.text and ent.text not in cleaned:
            cleaned += " " + ent.text

    # --- Step 4: Profanity filtering and final formatting ---
    cleaned = profanity.censor(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # --- Step 5: Ensure we don't over-clean (keep at least 75% of tokens) ---
    original_tokens = original.split()
    cleaned_tokens = cleaned.split()

    if (
        not cleaned_tokens
        or len(cleaned_tokens) < max(1, len(original_tokens) * 0.75)
    ):
        return original

    return cleaned


def clean_with_nlp(comment: str) -> str:
    """
    Unified cleaning function to be called by the processing pipeline.
    Returns cleaned comment (or original if cleaning fails).
    """
    try:
        cleaned = conservative_clean(comment)
        if not cleaned:
            return comment.strip()
        return cleaned
    except Exception as e:
        print(f"⚠️ Cleaning failed for text: {comment[:60]}... | Error: {e}")
        return comment.strip()
