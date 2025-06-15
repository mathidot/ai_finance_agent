# --- Import Summary Report Generator ---
from work_flow import app
from src.config import app_config
from typing import List
from src.utils.logging_config import setup_logger

try:
    from src.utils.summary_report import print_summary_report
    from src.utils.agent_collector import store_final_state, get_enhanced_final_state
    HAS_SUMMARY_REPORT = True
except ImportError:
    HAS_SUMMARY_REPORT = False

# --- Import Structured Terminal Output ---
try:
    from src.utils.structured_terminal import print_structured_output
    HAS_STRUCTURED_OUTPUT = True
except ImportError:
    HAS_STRUCTURED_OUTPUT = False

logger = setup_logger("hedge_fund")

# --- Run the Hedge Fund Workflow ---
def run_hedge_fund(
    run_id: str,
    tickers: List[str],
    start_date: str,
    end_date: str,
    portfolio: dict,
    show_reasoning: bool = False,
    num_of_news: int = 5,
    show_summary: bool = False
):
    """
    Stock analysis based on holdings information
    """
    logger.info(f"--- Starting Workflow Run ID: {run_id} ---")
    try:
        from backend.state import api_state
        api_state.current_run_id = run_id
        logger.info(f"--- API State updated with Run ID: {run_id} ---")
    except Exception as e:
        logger.info(f"Note: Could not update API state: {str(e)}")

    num_tickers: int = app_config.get("num_of_tickers", 10) - len(tickers)
    tickers: List[str] = get_bullish_ashares(num_tickers)
    
    initial_state = {
        "messages": [],  # 初始消息为空
        "data": {
            "tickers": tickers,
            "portfolio": portfolio,
            "start_date": start_date,
            "end_date": end_date,
            "num_of_news": num_of_news,
        },
        "metadata": {
            "show_reasoning": show_reasoning,
            "run_id": run_id,
            "show_summary": show_summary,
        }
    }

    try:
        from backend.utils.context_managers import workflow_run
        with workflow_run(run_id):
            final_state = app.invoke(initial_state)
            logger.info(f"--- Finished Workflow Run ID: {run_id} ---")

            if HAS_SUMMARY_REPORT and show_summary:
                store_final_state(final_state)
                enhanced_state = get_enhanced_final_state()
                print_summary_report(enhanced_state)

            if HAS_STRUCTURED_OUTPUT and show_reasoning:
                print_structured_output(final_state)
    except ImportError:
        final_state = app.invoke(initial_state)
        logger.info(f"--- Finished Workflow Run ID: {run_id} ---")

        if HAS_SUMMARY_REPORT and show_summary:
            store_final_state(final_state)
            enhanced_state = get_enhanced_final_state()
            print_summary_report(enhanced_state)

        if HAS_STRUCTURED_OUTPUT and show_reasoning:
            print_structured_output(final_state)
        try:
            api_state.complete_run(run_id, "completed")
        except Exception:
            pass
    return final_state["messages"][-1].content