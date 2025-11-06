import re, emoji, ftfy
from textblob import TextBlob
from better_profanity import profanity
import spacy

nlp = spacy.load("en_core_web_sm")
profanity.load_censor_words()

def clean_with_nlp(text: str) -> str:
    text = ftfy.fix_text(text)
    text = emoji.replace_emoji(text, replace='')
    text = re.sub(r"http\S+|www\S+", "", text)
    doc = nlp(text)
    tokens = [t.lemma_.lower() for t in doc if not t.is_stop and not t.is_punct and t.is_alpha and len(t.text) > 2]
    corrected = TextBlob(" ".join(tokens)).correct()
    cleaned = profanity.censor(str(corrected))
    return re.sub(r"\s+", " ", cleaned).strip()
