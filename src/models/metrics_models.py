from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

class RetrievalMetrics(BaseModel):
    with_llm_reranking: float
    retrieval_only: float
    improvement: float

class RecallMetrics(BaseModel):
    with_llm: float
    retrieval_only: float
    improvement: float

class ResponseTimeMetrics(BaseModel):
    with_llm_explanations: float
    without_llm: float
    overhead: float

class QualityMetrics(BaseModel):
    explanation_relevance: float
    human_reviewers: int
    scale: str

class TestMetrics(BaseModel):
    coverage_percentage: float
    total_tests: Optional[int]
    passing_tests: Optional[int]

class SystemMetrics(BaseModel):
    retrieval_accuracy: RetrievalMetrics
    recall: RecallMetrics
    response_time: ResponseTimeMetrics
    explanation_relevance: QualityMetrics
    test_coverage: TestMetrics
    last_updated: str
    system_version: str = "1.0.0"

class PerformanceTrend(BaseModel):
    date: str
    retrieval_accuracy: float
    recall: float
    response_time: float
    explanation_relevance: float

class MetricsSummary(BaseModel):
    overall_score: float
    top_performing_area: str
    areas_for_improvement: List[str]
    recommendations: List[str] 