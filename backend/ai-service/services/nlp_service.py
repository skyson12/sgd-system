import spacy
import openai
import os
from typing import Dict, List, Any
import logging
from schemas import NLPAnalysis

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        self.en_nlp = None
        self.es_nlp = None
        
        # OpenAI configuration
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    async def initialize(self):
        """Initialize NLP models"""
        try:
            logger.info("Loading spaCy models...")
            self.en_nlp = spacy.load("en_core_web_sm")
            self.es_nlp = spacy.load("es_core_news_sm")
            logger.info("NLP models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if NLP service is ready"""
        return self.en_nlp is not None and self.es_nlp is not None
    
    async def analyze_text(self, text: str) -> NLPAnalysis:
        """Perform comprehensive NLP analysis"""
        try:
            # Detect language
            language = await self._detect_language(text)
            
            # Select appropriate model
            nlp = self.es_nlp if language == "es" else self.en_nlp
            
            # Process text
            doc = nlp(text[:1000000])  # Limit text length for processing
            
            # Extract entities
            entities = self._extract_entities(doc)
            
            # Extract keywords
            keywords = self._extract_keywords(doc)
            
            # Simple sentiment analysis (can be enhanced)
            sentiment = await self._analyze_sentiment(text)
            
            return NLPAnalysis(
                entities=entities,
                language=language,
                sentiment=sentiment,
                keywords=keywords
            )
            
        except Exception as e:
            logger.error(f"NLP analysis failed: {e}")
            raise
    
    async def generate_summary(self, text: str, max_tokens: int = 200) -> str:
        """Generate text summary using OpenAI"""
        try:
            if not text.strip():
                return ""
            
            # Truncate text if too long
            max_input_length = 3000
            if len(text) > max_input_length:
                text = text[:max_input_length] + "..."
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates concise summaries of documents. Summarize the key points in a clear, professional manner."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize the following text:\n\n{text}"
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Summary generation failed"
    
    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extract named entities from spaCy doc"""
        entities = {}
        
        for ent in doc.ents:
            entity_type = ent.label_
            entity_text = ent.text.strip()
            
            if entity_type not in entities:
                entities[entity_type] = []
            
            if entity_text not in entities[entity_type]:
                entities[entity_type].append(entity_text)
        
        return entities
    
    def _extract_keywords(self, doc, limit: int = 10) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction based on token frequency and POS tags
        keywords = []
        
        # Filter tokens (nouns, proper nouns, adjectives)
        filtered_tokens = [
            token.lemma_.lower() for token in doc
            if (token.pos_ in ["NOUN", "PROPN", "ADJ"] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2)
        ]
        
        # Count frequency
        from collections import Counter
        token_freq = Counter(filtered_tokens)
        
        # Get most common tokens
        keywords = [token for token, freq in token_freq.most_common(limit)]
        
        return keywords
    
    async def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Basic language detection - could be improved with langdetect
        spanish_indicators = ["el", "la", "de", "en", "a", "con", "por", "para", "es", "está"]
        english_indicators = ["the", "and", "of", "to", "a", "in", "for", "is", "on", "that"]
        
        text_lower = text.lower()
        spanish_count = sum(1 for word in spanish_indicators if word in text_lower)
        english_count = sum(1 for word in english_indicators if word in text_lower)
        
        return "es" if spanish_count > english_count else "en"
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Basic sentiment analysis"""
        try:
            # This is a placeholder - could integrate with a proper sentiment analysis service
            # For now, return neutral sentiment
            return {
                "positive": 0.5,
                "negative": 0.3,
                "neutral": 0.2
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"neutral": 1.0}