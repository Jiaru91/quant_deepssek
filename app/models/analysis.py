from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base
from datetime import datetime

class AnalysisResult(Base):
    __tablename__ = "analysis_result"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    news_analysis = Column(Text)
    financial_analysis = Column(Text)
    prediction = Column(Text)
    confidence_score = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
