from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import logging
from typing import Dict, List
from schemas import ClassificationResult

logger = logging.getLogger(__name__)

class ClassificationService:
    def __init__(self):
        self.classifier = None
        self.categories = [
            "contract", "invoice", "report", "correspondence", 
            "legal", "financial", "technical", "administrative",
            "hr", "marketing", "other"
        ]
        
    async def initialize(self):
        """Initialize classification model"""
        try:
            # For now, create a simple rule-based classifier
            # In production, you'd load a pre-trained model
            self.classifier = self._create_rule_based_classifier()
            logger.info("Classification service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize classification service: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if classification service is ready"""
        return self.classifier is not None
    
    async def classify_document(self, text: str, title: str = "") -> ClassificationResult:
        """Classify document based on content and title"""
        try:
            combined_text = f"{title} {text}".lower()
            
            # Rule-based classification
            category, confidence = self._rule_based_classify(combined_text)
            
            # Extract relevant tags
            tags = self._extract_tags(combined_text)
            
            return ClassificationResult(
                category=category,
                confidence=confidence,
                tags=tags
            )
            
        except Exception as e:
            logger.error(f"Document classification failed: {e}")
            return ClassificationResult(
                category="other",
                confidence=0.1,
                tags=[]
            )
    
    def _create_rule_based_classifier(self):
        """Create a simple rule-based classifier"""
        return {
            "contract": ["contract", "agreement", "terms", "conditions", "liability", "clause"],
            "invoice": ["invoice", "bill", "payment", "amount", "total", "due", "tax"],
            "report": ["report", "analysis", "summary", "findings", "conclusion", "data"],
            "correspondence": ["dear", "sincerely", "regards", "letter", "email", "message"],
            "legal": ["legal", "law", "court", "judge", "attorney", "lawsuit", "litigation"],
            "financial": ["financial", "budget", "revenue", "profit", "expense", "cost"],
            "technical": ["technical", "specification", "manual", "guide", "procedure"],
            "administrative": ["policy", "procedure", "memo", "notice", "announcement"],
            "hr": ["employee", "salary", "benefits", "vacation", "performance", "hiring"],
            "marketing": ["marketing", "campaign", "promotion", "advertising", "brand"]
        }
    
    def _rule_based_classify(self, text: str) -> tuple[str, float]:
        """Classify using rule-based approach"""
        scores = {}
        
        for category, keywords in self.classifier.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        # Find category with highest score
        if max(scores.values()) == 0:
            return "other", 0.1
        
        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category] / len(self.classifier[best_category]), 1.0)
        
        # Ensure minimum confidence
        confidence = max(confidence, 0.1)
        
        return best_category, confidence
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text"""
        tags = []
        
        # Common document tags
        tag_keywords = {
            "urgent": ["urgent", "asap", "immediate", "priority"],
            "confidential": ["confidential", "private", "restricted", "sensitive"],
            "draft": ["draft", "preliminary", "version", "v1", "v2"],
            "final": ["final", "approved", "completed", "signed"],
            "expired": ["expired", "overdue", "past due"],
            "pending": ["pending", "awaiting", "in progress"]
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        return tags[:5]  # Limit to 5 tags