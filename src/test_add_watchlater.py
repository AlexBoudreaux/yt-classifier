import logging
import asyncio
from src.js_operations import add_watchlater_to_temp

# Configure logging
logging.basicConfig(filename='test_add_watchlater.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

async def test_add_watchlater_to_temp():
    logging.info("Starting test for add_watchlater_to_temp")
    try:
        await add_watchlater_to_temp()
        logging.info("add_watchlater_to_temp executed successfully")
    except Exception as e:
        logging.error(f"An error occurred during the test: {str(e)}", exc_info=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_add_watchlater_to_temp())
