import os
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.tools import tool
import yfinance as yf
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser

duckduckgo_search_tool = DuckDuckGoSearchRun()
# YFinance Tools (Custom implementations as before)
@tool
def get_stock_price(ticker: str) -> str:
    """Fetches the current stock price for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if not data.empty:
            return f"Current stock price for {ticker}: ${data['Close'].iloc[0]:.2f}"
        else:
            return f"Could not retrieve stock price for {ticker}."
    except Exception as e:
        return f"Error fetching stock price for {ticker}: {e}"

@tool
def get_analyst_recommendations(ticker: str) -> str:
    """Fetches analyst recommendations for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations
        if recommendations is not None and not recommendations.empty:
            # Format as a table (or part of a larger table)
            return f"Analyst Recommendations for {ticker}:\n{recommendations.to_markdown(index=False)}"
        else:
            return f"No analyst recommendations found for {ticker}."
    except Exception as e:
        return f"Error fetching analyst recommendations for {ticker}: {e}"

@tool
def get_stock_fundamentals(ticker: str) -> str:
    """Fetches key stock fundamentals for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        fundamental_data = {
            "Market Cap": info.get("marketCap"),
            "Trailing P/E": info.get("trailingPE"),
            "Forward P/E": info.get("forwardPE"),
            "Dividend Yield": info.get("dividendYield"),
            "Beta": info.get("beta"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Full Time Employees": info.get("fullTimeEmployees"),
        }
        # Filter out None values and format for display
        formatted_data = []
        for key, value in fundamental_data.items():
            if value is not None:
                if isinstance(value, (int, float)):
                    if "Yield" in key:
                        formatted_data.append(f"| {key} | {value:.2%} |")
                    elif "Cap" in key:
                        formatted_data.append(f"| {key} | ${value:,.0f} |")
                    else:
                        formatted_data.append(f"| {key} | {value:.2f} |")
                else:
                    formatted_data.append(f"| {key} | {value} |")

        if formatted_data:
            header = "| Metric | Value |\n|---|---|"
            return f"Key Fundamentals for {ticker}:\n{header}\n" + "\n".join(formatted_data)
        else:
            return f"No fundamental data found for {ticker}."
    except Exception as e:
        return f"Error fetching stock fundamentals for {ticker}: {e}"

# Combine all tools
tools = [
    duckduckgo_search_tool,
    get_stock_price,
    get_analyst_recommendations,
    get_stock_fundamentals,
]

prompt = hub.pull("hwchase17/react")
custom_instructions = """
Always use tables to display financial/numerical data.
For text data use bullet points and small paragraphs.
You are a helpful Qwen Finance Agent.
"""
final_prompt = PromptTemplate.from_template(
    custom_instructions + "\n" + prompt.template
)

llm = ChatTongyi(
    model_name="qwen-turbo",
    temperature=0.0
)

agent_chain = create_react_agent(llm, tools, final_prompt)
agent_executor = AgentExecutor(
    agent=agent_chain,
    tools=tools,
    verbose=True, # Shows tool calls and intermediate steps
    handle_parsing_errors=True # Good practice for robust agents
)

if __name__ == "__main__":
    print("--- Testing Qwen Finance Agent Directly ---")
    test_queries = [
        "What is the stock price of AAPL?",
        "What are the analyst recommendations for MSFT?",
        "Can you tell me the fundamental data for GOOG?",
        "Search for recent news about Alibaba.", # Uses DuckDuckGo
        "Provide me with the stock price for BABA and its analyst recommendations."
    ]
    for query in test_queries:
        print(f"\nUser Query: {query}")
        try:
            response = agent_executor.invoke({"input": query})
            print(f"Agent Response:\n{response['output']}")
        except Exception as e:
            print(f"An error occurred while processing '{query}': {e}")
            print("Please ensure your DASHSCOPE_API_KEY is correctly set in your environment variables.")