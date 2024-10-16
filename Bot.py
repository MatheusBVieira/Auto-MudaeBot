import Vars
import time
import schedule
from Function import simpleRoll, check_claim_status

def schedule_next_roll():
    """Ajustar o horário da próxima rolagem com base no status dos rolls"""
    remaining_claim_time, rolls_ready, rolls_available = check_claim_status()

    next_roll_in_minutes = rolls_ready if rolls_ready > 0 else 60  # Próxima rolagem será em `rolls_ready` minutos
    if rolls_available > 0:  # Verificar se há rolls disponíveis
        print(f"Você tem {rolls_available} rolls disponíveis. Executando rolls")
        simpleRoll()
    else:
        print("Sem rolls disponíveis no momento.")

    print(f"Setando schedule para próximo roll que será em {next_roll_in_minutes} minutos.")
    schedule.clear()  # Limpar qualquer agendamento anterior
    schedule.every(next_roll_in_minutes).minutes.do(schedule_next_roll)
# Iniciar o bot consultando o status dos rolls
schedule_next_roll()

# Loop principal para executar o agendamento
while True:
    schedule.run_pending()
    time.sleep(1)
