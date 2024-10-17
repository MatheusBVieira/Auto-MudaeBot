import Vars
import time
import schedule
from Function import simpleRoll, check_claim_status
from Texts import Texts
import logging
import random

HIGHLIGHT = '\033[93m\033[1m'
MAGENTA = '\033[35m'
RESET = '\033[0m'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def schedule_next_roll_for_server(server_name):
    server_config = Vars.servers[server_name]
    Texts.set_language(server_config['language'])
    
    logging.info(MAGENTA + f"------ Checking claim status and rolls for server {server_name} ------" + RESET)
    remaining_claim_time, rolls_ready, rolls_available, can_claim = check_claim_status(server_config)

    next_roll_in_minutes = rolls_ready if rolls_ready > 0 else 60
    if rolls_available > 0:
        logging.info(HIGHLIGHT + f"You have {rolls_available} rolls available on server {server_name}. Rolling now." + RESET)
        kakera_threshold = server_config['kakeraThresholdNormal']
        simpleRoll(remaining_claim_time, rolls_available, kakera_threshold, can_claim, server_config)
    else:
        logging.info(f"No rolls available at the moment on server {server_name}.")

    random_number = random.randint(5, 20)
    logging.info(HIGHLIGHT + f"Scheduling the next roll in {next_roll_in_minutes} minutes plus {random_number} on server {server_name}." + RESET)
    schedule.clear()
    schedule.every(next_roll_in_minutes + random_number).minutes.do(schedule_next_roll_for_server, server_name)

for server_name in Vars.servers:
    logging.info(MAGENTA + f"-------- Starting roll scheduler for server {server_name} --------" + RESET)
    schedule_next_roll_for_server(server_name)
    time.sleep(2)

while True:
    schedule.run_pending()
    time.sleep(1)
