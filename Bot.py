import Vars
import time
import schedule
from Function import simpleRoll, check_claim_status
from Texts import Texts

Texts.set_language('ENGLISH')

def schedule_next_roll():
    """Ajustar o horário da próxima rolagem com base no status dos rolls"""
    remaining_claim_time, rolls_ready, rolls_available, can_claim = check_claim_status()

    next_roll_in_minutes = rolls_ready if rolls_ready > 0 else 60
    if rolls_available > 0:
        print(f"Você tem {rolls_available} rolls disponíveis. Executando rolls")
        kakera_threshold = Vars.kakeraThresholdFinalHour if remaining_claim_time <= 60 else Vars.kakeraThresholdNormal
        simpleRoll(remaining_claim_time, rolls_available, kakera_threshold, can_claim)
    else:
        print("Sem rolls disponíveis no momento.")

    print(f"Setando schedule para próximo roll que será em {next_roll_in_minutes} minutos.")
    schedule.clear()
    schedule.every(next_roll_in_minutes).minutes.do(schedule_next_roll)

schedule_next_roll()

while True:
    schedule.run_pending()
    time.sleep(1)
