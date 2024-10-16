import Vars
import time
import schedule
from Function import simpleRoll, check_claim_status
from Texts import Texts
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

Texts.set_language('ENGLISH')
logging.info("Language set to English")

def schedule_next_roll():
    """Ajustar o horário da próxima rolagem com base no status dos rolls"""
    logging.info("Checking claim status and rolls")
    remaining_claim_time, rolls_ready, rolls_available, can_claim = check_claim_status()

    next_roll_in_minutes = rolls_ready if rolls_ready > 0 else 60
    if rolls_available > 0:
        logging.info(f"You have {rolls_available} rolls available. Rolling now.")
        kakera_threshold = Vars.kakeraThresholdFinalHour if remaining_claim_time <= 60 else Vars.kakeraThresholdNormal
        simpleRoll(remaining_claim_time, rolls_available, kakera_threshold, can_claim)
    else:
        logging.info("No rolls available at the moment.")

    logging.info(f"Scheduling the next roll in {next_roll_in_minutes} minutes.")
    schedule.clear()
    schedule.every(next_roll_in_minutes).minutes.do(schedule_next_roll)

logging.info("Starting roll scheduler")
schedule_next_roll()

while True:
    schedule.run_pending()
    time.sleep(1)
