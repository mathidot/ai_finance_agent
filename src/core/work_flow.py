# --- Agent Imports ---
from src.agents.valuation import valuation_agent
from src.agents.state import AgentState
from src.agents.sentiment import sentiment_agent
from src.agents.risk_manager import risk_management_agent
from src.agents.technicals import technical_analyst_agent
from src.agents.portfolio_manager import portfolio_management_agent
from src.agents.market_data import market_data_agent
from src.agents.fundamentals import fundamentals_agent
from src.agents.researcher_bull import researcher_bull_agent
from src.agents.researcher_bear import researcher_bear_agent
from src.agents.debate_room import debate_room_agent
from src.agents.macro_analyst import macro_analyst_agent
from src.agents.macro_news_agent import macro_news_agent
from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage

# --- Define the Workflow Graph ---
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("market_data_agent", market_data_agent)
workflow.add_node("technical_analyst_agent", technical_analyst_agent)
workflow.add_node("fundamentals_agent", fundamentals_agent)
workflow.add_node("sentiment_agent", sentiment_agent)
workflow.add_node("valuation_agent", valuation_agent)
workflow.add_node("macro_news_agent", macro_news_agent)  # 新闻 agent
workflow.add_node("researcher_bull_agent", researcher_bull_agent)
workflow.add_node("researcher_bear_agent", researcher_bear_agent)
workflow.add_node("debate_room_agent", debate_room_agent)
workflow.add_node("risk_management_agent", risk_management_agent)
workflow.add_node("macro_analyst_agent", macro_analyst_agent)
workflow.add_node("portfolio_management_agent", portfolio_management_agent)

# Set entry point
workflow.set_entry_point("market_data_agent")

# Edges from market_data_agent to the five parallel agents
workflow.add_edge("market_data_agent", "technical_analyst_agent")
workflow.add_edge("market_data_agent", "fundamentals_agent")
workflow.add_edge("market_data_agent", "sentiment_agent")
workflow.add_edge("market_data_agent", "valuation_agent")
# macro_news_agent 也从 market_data_agent 并行出来
workflow.add_edge("market_data_agent", "macro_news_agent")

# Main analysis path (technical, fundamentals, sentiment, valuation -> researchers -> ... -> macro_analyst)
workflow.add_edge("technical_analyst_agent", "researcher_bull_agent")
workflow.add_edge("fundamentals_agent", "researcher_bull_agent")
workflow.add_edge("sentiment_agent", "researcher_bull_agent")
workflow.add_edge("valuation_agent", "researcher_bull_agent")

workflow.add_edge("technical_analyst_agent", "researcher_bear_agent")
workflow.add_edge("fundamentals_agent", "researcher_bear_agent")
workflow.add_edge("sentiment_agent", "researcher_bear_agent")
workflow.add_edge("valuation_agent", "researcher_bear_agent")

workflow.add_edge("researcher_bull_agent", "debate_room_agent")
workflow.add_edge("researcher_bear_agent", "debate_room_agent")

workflow.add_edge("debate_room_agent", "risk_management_agent")
workflow.add_edge("risk_management_agent", "macro_analyst_agent")

# Edges to portfolio_management_agent (汇聚点)
# macro_analyst_agent (end of main analysis path) and macro_news_agent (parallel news path)
# both feed into portfolio_management_agent.
# LangGraph will wait for both parent nodes to complete before running portfolio_management_agent.
workflow.add_edge("macro_analyst_agent", "portfolio_management_agent")
workflow.add_edge("macro_news_agent", "portfolio_management_agent")

# Final node
workflow.add_edge("portfolio_management_agent", END)

app = workflow.compile()

