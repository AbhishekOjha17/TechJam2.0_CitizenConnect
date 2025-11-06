import torch, os, time
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sentence_transformers import SentenceTransformer
from huggingface_hub import constants

os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "300"
constants.HF_HUB_DOWNLOAD_TIMEOUT = 300

device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model_with_retry(loader_func, model_name, max_retries=5, retry_delay=10):
    for attempt in range(max_retries):
        try:
            return loader_func()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))
            else:
                raise e

# Load all models once
embedder = load_model_with_retry(lambda: SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device), "Embedder")
sent_tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
sent_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest").to(device)
z_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
z_model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli").to(device)

TAG_LABELS = [
    "water purity and contamination", "road potholes and cracks", "non-functional street light outage",
    "irregular garbage pickup schedule", "frequent power cuts and load shedding", "bus/train delays and cancellations"
]

def sentiment(text):
    tokens = sent_tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
    with torch.no_grad():
        output = sent_model(**tokens)
    scores = output.logits.softmax(dim=1).detach().cpu().numpy()[0]
    labels = ["negative", "neutral", "positive"]
    return labels[int(scores.argmax())], float(scores.max())

def urgency_score(text):
    text = text.lower()
    if any(w in text for w in ["emergency", "critical", "unsafe"]):
        return "CRITICAL_LEVEL_3", 5
    elif any(w in text for w in ["urgent", "immediately", "severe"]):
        return "HIGH_LEVEL_2", 3
    elif any(w in text for w in ["frequent", "daily", "worsening"]):
        return "MEDIUM_LEVEL_1", 1
    return "LOW_LEVEL_0", 0

def zero_shot(text):
    hypothesis_templates = [f"This issue is related to {label}." for label in TAG_LABELS]
    probs = []
    for hyp in hypothesis_templates:
        tokens = z_tokenizer(text, hyp, return_tensors="pt", truncation=True).to(device)
        with torch.no_grad():
            logits = z_model(**tokens).logits
        entailment_prob = logits.softmax(dim=1)[0, 2].item()
        probs.append((hyp, entailment_prob))
    top = sorted(probs, key=lambda x: x[1], reverse=True)[:3]
    return [[t[0].replace("This issue is related to ", "").strip("."), round(t[1], 3)] for t in top]

def calculate_priority(s_label, s_conf, u_score, rating):
    raw = u_score + (5 - rating) + (2 if s_label == "negative" else 0)
    if raw >= 8: return "P1_CRITICAL", raw
    elif raw >= 5: return "P2_HIGH", raw
    elif raw >= 3: return "P3_MEDIUM", raw
    return "P4_LOW", raw

def model_output_from_text(text, rating=3):
    s_label, s_conf = sentiment(text)
    u_label, u_score = urgency_score(text)
    p_label, p_raw = calculate_priority(s_label, s_conf, u_score, rating)
    tags = zero_shot(text)
    emb = embedder.encode(text, convert_to_tensor=False).tolist()

    return {
        # "embedding": emb,
        "sentiment": s_label,
        "sentiment_confidence": round(s_conf, 3),
        "urgency_label": u_label,
        "urgency_score": u_score,
        "priority_label": p_label,
        "priority_raw_score": p_raw,
        "tags_with_confidence": tags
    }
