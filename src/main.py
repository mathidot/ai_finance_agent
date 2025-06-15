import sys
import argparse
import uuid  # Import uuid for run IDs
import threading  # Import threading for background task
import uvicorn  # Import uvicorn to run FastAPI

from datetime import datetime, timedelta
from typing import List

# --- Logging and Backend Imports ---
from src.utils.output_logger import OutputLogger
from src.utils.llm_interaction_logger import (
    log_agent_execution,
    set_global_log_storage
)
from backend.dependencies import get_log_storage
from backend.main import app as fastapi_app
from src.utils.logging_config import setup_logger
from src.core.hedge_fund import run_hedge_fund

# --- Initialize Logging ---
log_storage = get_log_storage()
set_global_log_storage(log_storage)
sys.stdout = OutputLogger()
logger = setup_logger('main_workflow')

# --- FastAPI Background Task ---
def run_fastapi():
    print("--- Starting FastAPI server in background (port 8000) ---")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_config=None)

# --- Main Execution Block ---
if __name__ == "__main__":
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    parser = argparse.ArgumentParser(
        description='Run the hedge fund trading system')
    parser.add_argument('--ticker', type=str, required=True,
                        help='Stock ticker symbol')
    parser.add_argument('--start-date', type=str,
                        help='Start date (YYYY-MM-DD). Defaults to 1 year before end date')
    parser.add_argument('--end-date', type=str,
                        help='End date (YYYY-MM-DD). Defaults to yesterday')
    parser.add_argument('--show-reasoning', action='store_true',
                        help='Show reasoning from each agent')
    parser.add_argument('--num-of-news', type=int, default=5,
                        help='Number of news articles to analyze for sentiment (default: 5)')
    parser.add_argument('--initial-capital', type=float, default=100000.0,
                        help='Initial cash amount (default: 100,000)')
    parser.add_argument('--initial-position', type=int,
                        default=0, help='Initial stock position (default: 0)')
    parser.add_argument('--summary', action='store_true',
                        help='Show beautiful summary report at the end')
    args = parser.parse_args()
    current_date = datetime.now()
    yesterday = current_date - timedelta(days=1)
    end_date = yesterday if not args.end_date else min(
        datetime.strptime(args.end_date, '%Y-%m-%d'), yesterday)
    if not args.start_date:
        start_date = end_date - timedelta(days=365)
    else:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    if start_date > end_date:
        raise ValueError("Start date cannot be after end date")
    if args.num_of_news < 1:
        raise ValueError("Number of news articles must be at least 1")
    if args.num_of_news > 100:
        raise ValueError("Number of news articles cannot exceed 100")
    portfolio = {"cash": args.initial_capital, "stock": args.initial_position}
    main_run_id = str(uuid.uuid4())
    result = run_hedge_fund(
        run_id=main_run_id,
        ticker=[args.ticker],
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        portfolio=portfolio,
        show_reasoning=args.show_reasoning,
        num_of_news=args.num_of_news,
        show_summary=args.summary
    )
    print("\nFinal Result:")
    print(result)
