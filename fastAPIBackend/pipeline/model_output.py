# pipeline/model_output.py

import torch, os, time
from datetime import datetime
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sentence_transformers import SentenceTransformer
from huggingface_hub import constants

# ==============================
# CONFIG
# ==============================

os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "300"
constants.HF_HUB_DOWNLOAD_TIMEOUT = 300

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"✅ Using device: {device}")

# ==============================
# RETRY LOGIC
# ==============================

def load_model_with_retry(loader_func, model_name, max_retries=5, retry_delay=10):
    """Load a model with retry logic (used for HF network stability)."""
    for attempt in range(max_retries):
        try:
            print(f"Loading {model_name} (attempt {attempt + 1}/{max_retries})...")
            return loader_func()
        except Exception as e:
            if attempt < max_retries - 1:
                wait = retry_delay * (2 ** attempt)
                print(f"⚠️ Failed to load {model_name}: {str(e)[:100]}... Retrying in {wait}s")
                time.sleep(wait)
            else:
                print(f"❌ Could not load {model_name} after {max_retries} attempts.")
                raise e

# ==============================
# MODEL INITIALIZATION
# ==============================

# Sentence Embeddings
embedder = load_model_with_retry(
    lambda: SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device),
    "Sentence Embedder"
)

# Sentiment Analysis
sent_model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
sent_tokenizer = load_model_with_retry(lambda: AutoTokenizer.from_pretrained(sent_model_name), "Sentiment Tokenizer")
sent_model = load_model_with_retry(lambda: AutoModelForSequenceClassification.from_pretrained(sent_model_name).to(device), "Sentiment Model")

# Zero-Shot Classification
z_model_name = "facebook/bart-large-mnli"
z_tokenizer = load_model_with_retry(lambda: AutoTokenizer.from_pretrained(z_model_name), "Zero-Shot Tokenizer")
z_model = load_model_with_retry(lambda: AutoModelForSequenceClassification.from_pretrained(z_model_name).to(device), "Zero-Shot Classifier")

# ==============================
# TAG LABELS
# ==============================

HIGH_PRIORITY_LABELS = [
    "critical sewage overflow and public health risk", "exposed high-tension electrical wiring", 
    "major structural collapse or building safety hazard", "contaminated drinking water leading to sickness",
    "unattended road accident site", "total closure of main arterial road", "severe flash flooding risk due_to drainage",
]

CORE_ISSUE_LABELS = [
    "water purity and contamination", "inconsistent water pressure", "pipe leakage and water wastage",
    "road potholes and cracks", "faded road markings or signs", "illegal encroachment on road shoulder",
    "frequent power cuts and load shedding", "voltage fluctuations and power instability",
    "broken or unsynchronized traffic signals", "persistent traffic jams and congestion",
    "irregular garbage pickup schedule", "overflowing public bins and dumping grounds",
    "bus/train delays and cancellations", "non-functional street light outage",
]

BROAD_LABELS = [
    "municipal administrative delay and poor communication", "misconduct or corruption by civic staff",
    "general civic body performance rating", "noise pollution and public nuisance",
]

TAG_LABELS = HIGH_PRIORITY_LABELS + CORE_ISSUE_LABELS + BROAD_LABELS

print(f"✅ Total Zero-Shot Tags Loaded: {len(TAG_LABELS)}")

# ==============================
# MODEL FUNCTIONS
# ==============================

def sentiment(text: str):
    """Classifies text sentiment as negative, neutral, or positive."""
    tokens = sent_tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
    with torch.no_grad():
        output = sent_model(**tokens)
    probs = output.logits.softmax(dim=1).cpu().numpy()[0]
    labels = ["negative", "neutral", "positive"]
    return labels[int(probs.argmax())], float(probs.max())


def urgency_score(text: str):
    """Assign urgency level using keyword-based heuristic."""
    critical = ["emergency", "critical", "unsafe", "fire", "collapse", "disaster", "life threatening", "crisis"]
    high = ["urgent", "immediately", "severe", "major", "asap", "unbearable", "health risk"]
    medium = ["frequent", "daily", "delay", "worsening", "long time", "inconvenience"]

    text = text.lower()
    score = 0
    score += sum(3 for w in critical if w in text)
    score += sum(2 for w in high if w in text)
    score += sum(1 for w in medium if w in text)

    if score >= 8: return "CRITICAL_LEVEL_3", score
    elif score >= 4: return "HIGH_LEVEL_2", score
    elif score >= 1: return "MEDIUM_LEVEL_1", score
    return "LOW_LEVEL_0", 0


def zero_shot(text: str):
    """Performs Zero-Shot classification using expanded TAG_LABELS."""
    hypotheses = [f"This issue is related to {label}." for label in TAG_LABELS]
    probs = []

    for hyp in hypotheses:
        tokens = z_tokenizer(text, hyp, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
        with torch.no_grad():
            logits = z_model(**tokens).logits
        entailment_prob = logits.softmax(dim=1)[0, 2].item()
        probs.append((hyp, entailment_prob))

    sorted_probs = sorted(probs, key=lambda x: x[1], reverse=True)
    threshold = 0.5
    top = [(p[0].replace("This issue is related to ", "").strip("."), round(p[1], 3)) for p in sorted_probs if p[1] > threshold]
    if not top:
        top = [(sorted_probs[0][0].replace("This issue is related to ", "").strip("."), round(sorted_probs[0][1], 3))]
    return top


def calculate_priority(sent_label, sent_conf, urg_score, rating, zero_tags):
    """Compute overall priority level for task escalation."""
    raw = urg_score
    if sent_label == "negative":
        raw += sent_conf * 2.5
    raw += (5 - rating) * 1.5
    if any(tag in zero_tags for tag in HIGH_PRIORITY_LABELS):
        raw += 5.0

    if raw >= 15: return "P1_CRITICAL", round(raw, 2)
    elif raw >= 8: return "P2_HIGH", round(raw, 2)
    elif raw >= 3: return "P3_MEDIUM", round(raw, 2)
    return "P4_LOW", round(raw, 2)


# ==============================
# MAIN ENTRY POINT
# ==============================

def model_output_from_text(text: str, rating: int = 3):
    """
    Central model entry for pipeline.
    - Sentiment analysis
    - Urgency scoring
    - Zero-shot tagging
    - Priority calculation
    - Embedding vector generation
    """

    if not text or not text.strip():
        return {"error": "Empty text"}

    # Step 1: Sentiment
    s_label, s_conf = sentiment(text)

    # Step 2: Urgency
    u_label, u_score = urgency_score(text)

    # Step 3: Zero-Shot Tagging
    tags = zero_shot(text)
    tag_names = [t[0] for t in tags]

    # Step 4: Priority
    p_label, p_raw = calculate_priority(s_label, s_conf, u_score, rating, tag_names)

    # Step 5: Embedding
    emb = embedder.encode(text, convert_to_tensor=False).tolist()

    # Step 6: Output Struct
    return {
        # "embedding": emb,  # uncomment if you want to store embeddings
        "sentiment": s_label,
        "sentiment_confidence": round(s_conf, 3),
        "urgency_label": u_label,
        "urgency_score": u_score,
        "priority_label": p_label,
        "priority_raw_score": p_raw,
        "tags_with_confidence": tags
    }
