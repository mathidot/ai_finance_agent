from typing import Dict, List, TypedDict, Literal
from src.utils.logging_config import setup_logger

logger = setup_logger("ticker_info")

class SignalInfo(TypedDict):
    """SignalInfo"""
    signal: Literal['bullish', 'bearish', 'neutral']
    details: str

class FundamentalAnalysis(TypedDict):
    """Fundamental Info"""
    signal: Literal['bullish', 'bearish', 'neutral']
    confidence: float
    reasoning: Dict[str, SignalInfo]

class StrategySignal(TypedDict):
    """StrategySignal Info"""
    signal: Literal['bullish', 'bearish', 'neutral']
    confidence: float
    metrics: Dict[str, float]

class AnalysisReport(TypedDict):
    """AnalysisReport Info"""
    signal: Literal['bullish', 'bearish', 'neutral']
    confidence: float
    strategy_signals: Dict[str, StrategySignal]

class TickerInfo(TypedDict):
    """store specific tickerInfo"""
    fundamental_analysis: FundamentalAnalysis
    analysis_report: AnalysisReport

class TickersInfo(TypedDict):
    """store all tickers info"""
    tickers_info: List[TickerInfo]