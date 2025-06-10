# backend/agent.py
import os
import yfinance as yf
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatTongyi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FinanceAgentService:
    def __init__(self):
        # Ensure DASHSCOPE_API_KEY is set
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.dashscope_api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable not set.")

        self.llm = ChatTongyi(
            model_name="qwen-turbo",
            temperature=0.0
        )

        self.tools = self._initialize_tools()
        self.agent_executor = self._initialize_agent()

    def _initialize_tools(self):
        # DuckDuckGo Tool
        duckduckgo_search_tool = DuckDuckGoSearchRun()

        # YFinance Tools
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
                    # Ensure recommendations table is clean for markdown
                    # Removing index for cleaner display
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

        return [
            duckduckgo_search_tool,
            get_stock_price,
            get_analyst_recommendations,
            get_stock_fundamentals,
        ]

    def _initialize_agent(self):
        prompt = hub.pull("hwchase17/react")
        custom_instructions = """
        Always use tables to display financial/numerical data.
        For text data use bullet points and small paragraphs.
        You are a helpful Qwen Finance Agent.
        """
        final_prompt = PromptTemplate.from_template(
            custom_instructions + "\n" + prompt.template
        )

        agent_chain = create_react_agent(self.llm, self.tools, final_prompt)
        agent_executor = AgentExecutor(
            agent=agent_chain,
            tools=self.tools,
            verbose=True, # Set to True for debugging in backend logs
            handle_parsing_errors=True
        )
        return agent_executor

    async def run_query(self, query: str) -> str:
        """Runs the query through the LangChain agent."""
        try:
            # LangChain's invoke method can be async or sync depending on underlying models/tools.
            # For simplicity with FastAPI, we'll await it.
            response = await self.agent_executor.ainvoke({"input": query})
            return response["output"]
        except Exception as e:
            # Log the error for backend debugging, but return a user-friendly message
            print(f"Error running agent query: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again or rephrase."

# Instantiate the service globally or in a dependency injection system for FastAPI
# This ensures the agent is initialized once.
try:
    finance_agent_service = FinanceAgentService()
except ValueError as e:
    print(f"Agent initialization error: {e}")
    print("Please set the DASHSCOPE_API_KEY environment variable.")
    finance_agent_service = None # Or handle more robustly, e.g., exit