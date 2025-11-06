from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
import uuid
 
class ModelOutput(BaseModel):
    sentiment: Optional[str]
    sentiment_confidence: Optional[float]
    urgency_label: Optional[str]
    urgency_score: Optional[int]
    priority_label: Optional[str]
    priority_raw_score: Optional[float]
    tags_with_confidence: Optional[List[List[Any]]]  # [["tag", 0.98], ...]


class Report(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    city: str
    timestamp: datetime
    rating: int
    comment: str
    public_service: str
    district: str

    # Optional user info
    device_location: Optional[str] = None
    is_anonymous: bool = True
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None

    # Image-related (optional, later)
    imgUrl: Optional[str] = None
    imgDesc: Optional[str] = None
    imgTag: Optional[List[str]] = None
    imgSeverity: Optional[int] = None

    # Later processing fields
    cleaned_comment: Optional[str] = None
    _model_output: Optional[ModelOutput] = None

    processing: Optional[int] = 0



class Stats(BaseModel):
    id: str = Field(default_factory=lambda: "global_stats")
    scope: str = Field(default="global")  # 'global' or 'district'
    district: Optional[str] = None

    # Average ratings
    avg_rating_overall: float = 0.0
    avg_rating_by_service: Dict[str, float] = {}

    # Sentiment counts
    sentiment_counts_overall: Dict[str, int] = {"positive": 0, "negative": 0, "neutral": 0}
    sentiment_counts_by_service: Dict[str, Dict[str, int]] = {}

    # Feedback counts
    total_feedback_overall: int = 0
    total_feedback_by_service: Dict[str, int] = {}

    feedback_over_time: Dict[str, int] = {}
    last_updated: datetime = Field(default_factory=datetime.utcnow)