import discum
import json
import time
import requests
import Vars
import re
from discum.utils.slash import SlashCommander

botID = '432610292342587392'  # ID do bot Mudae
auth = {'authorization': Vars.token}
bot = discum.Client(token=Vars.token, log=False)
url = f'https://discord.com/api/v8/channels/{Vars.channelId}/messages'

global_remaining_claim_time = 0
global_rolls_ready = 0
global_rolls_available = 0
global_can_claim = True

def check_claim_status():
    """Executar o comando $tu e analisar o tempo de claim e rolls"""
    bot.sendMessage(Vars.channelId, "$tu")
    time.sleep(2)  # Aguardar resposta do bot no Discord

    r = requests.get(url, headers=auth)
    response = json.loads(r.text)

    remaining_claim_time = 0
    rolls_ready = 0
    rolls_available = 0  # Novo: armazenar o número de rolls disponíveis
    can_claim = True

    for message in response:
        if 'claim' in message['content']:
            content = message['content']

            # Extração do tempo de reset de claim
            if "The next claim reset is in" in content:
                claim_time_string = content.split("The next claim reset is in **")[1]
                hours_minutes = claim_time_string.split("**")[0].strip()
                can_claim = True

                # Verifica se contém horas
                if 'h' in hours_minutes:
                    # Exemplo: "1h 10 min"
                    hours, minutes = map(int, re.findall(r'\d+', hours_minutes))
                    remaining_claim_time = hours * 60 + minutes
                else:
                    # Exemplo: "48 min"
                    minutes = int(re.search(r'\d+', hours_minutes).group())
                    remaining_claim_time = minutes

            # Extração de uma mensagem alternativa: "you can't claim for another"
            if "you can't claim for another" in content:
                claim_time_string = content.split("you can't claim for another **")[1]
                hours_minutes = claim_time_string.split("**")[0].strip()
                can_claim = False

                # Verifica se contém horas
                if 'h' in hours_minutes:
                    # Exemplo: "1h 10 min"
                    hours, minutes = map(int, re.findall(r'\d+', hours_minutes))
                    remaining_claim_time = hours * 60 + minutes
                else:
                    # Exemplo: "48 min"
                    minutes = int(re.search(r'\d+', hours_minutes).group())
                    remaining_claim_time = minutes

            # Extração do tempo de rolls
            if "Next rolls reset in" in content:
                rolls_time_string = content.split("Next rolls reset in **")[1]
                rolls_minutes = int(re.search(r'\d+', rolls_time_string).group())
                rolls_ready = rolls_minutes

            # Extração do número de rolls disponíveis
            if "You have" in content and "rolls left" in content:
                rolls_available = int(content.split("You have **")[1].split("**")[0].strip())

            global global_remaining_claim_time, global_rolls_ready, global_rolls_available, global_can_claim
            global_remaining_claim_time = remaining_claim_time
            global_rolls_ready = rolls_ready
            global_rolls_available = rolls_available
            global_can_claim = can_claim

            return remaining_claim_time, rolls_ready, rolls_available
    return remaining_claim_time, rolls_ready, rolls_available

def simpleRoll():
    print(time.strftime("Rolling at %H:%M - %d/%m/%y", time.localtime()))

    claimed = '❤️'
    unclaimed = '🤍'
    kakera = '💎'
    emoji='🐿️'

    # Utilizar as variáveis globais, sem precisar executar $tu de novo
    remaining_claim_time = global_remaining_claim_time
    rolls_ready = global_rolls_ready
    rolls_available = global_rolls_available

    is_last_hour = remaining_claim_time <= 60  # Última hora antes do reset
    if is_last_hour:
        kakera_threshold = Vars.kakeraThresholdFinalHour
    else:
        kakera_threshold = Vars.kakeraThresholdNormal

    rolled_cards = []

    for i in range(rolls_available): 
        rollCommand = SlashCommander(bot.getSlashCommands(botID).json()).get([Vars.rollCommand])
        bot.triggerSlashCommand(botID, Vars.channelId, Vars.serverId, data=rollCommand)
        time.sleep(1.8)

        # Após cada giro, analisar a carta
        r = requests.get(url, headers=auth)
        jsonCard = json.loads(r.text)

        for card in jsonCard:
            idMessage = card['id']
            try:
                cardName = card['embeds'][0]['author']['name']
                cardSeries = card['embeds'][0]['description'].split('**')[0]
                cardPower = int(card['embeds'][0]['description'].split('**')[1])
            except (IndexError, KeyError, ValueError):
                cardName = 'null'
                cardSeries = 'null'
                cardPower = 0

            if not 'footer' in card['embeds'][0] or not 'icon_url' in card['embeds'][0]['footer']:
                print(i,' - '+unclaimed+' ---- ',cardPower,' - '+cardName)
            else: 
                print(i,' - '+claimed+' ---- ',cardPower,' - '+cardName)

            # Verifica se a carta possui 'components' antes de acessar
            if 'components' in card and len(card['components']) > 0:
                components = card['components'][0]['components']
            else:
                components = []
            
            # Adiciona a primeira carta girada à lista
            rolled_cards.append({
                'id': idMessage,
                'name': cardName,
                'series': cardSeries,
                'power': cardPower,
                'components': components
            })

            # Interrompe o loop após adicionar a primeira carta
            break
        
    print('Rolling finalizado.')
    print('Iniciando analise das cartas...')

    highest_power = 0
    best_card_id = None
    best_card_name = None

    for card in rolled_cards:
        cardName = card['name']
        cardPower = card['power']
        cardSeries = card['series']

        if cardPower > highest_power:
            highest_power = cardPower
            best_card_id = card['id']
            best_card_name = cardName

        # Verificar e reagir ao Kakera
        components = card['components']
        if components:
            print('Buscando cartas com kakera para reagir')
            for index in range(len(components)):
                try:
                    # Verifique se existe emoji e se ele corresponde ao Kakera desejado
                    if 'emoji' in components[index] and components[index]['emoji']['name'] in Vars.desiredKakeras:
                        print(f'{kakera} - {kakera} - Trying to react to {components[index]["emoji"]["name"]} of {cardName}')
                        bot.click(card['author']['id'], channelID=card['channel_id'], guildID=Vars.serverId,
                                  messageID=card['id'], messageFlags=card['flags'],
                                  data={'component_type': 2, 'custom_id': components[index]['custom_id']})
                        time.sleep(0.5)
                except IndexError:
                    # Captura casos em que não há emoji ou componentes
                    print('Nenhuma carta com kakera para reagir')
                    continue

    print(f'is_last_hour: {is_last_hour}')
    if global_can_claim:
        if not is_last_hour:  # Nas primeiras duas horas
            if highest_power >= kakera_threshold:
                print(f'Trying to claim {cardName} with {cardPower} kakera')
                requests.put(f'https://discord.com/api/v8/channels/{Vars.channelId}/messages/{card["id"]}/reactions/%E2%9D%A4%EF%B8%8F/%40me', headers=auth)     
            else:
                print(f'Nenhuma carta com pode maior que {kakera_threshold} kakera')

        # Se estamos na última hora e a carta de maior valor foi encontrada
        if is_last_hour:
            print(f'Claiming best card {best_card_name} with {highest_power} kakera')
            requests.put(f'https://discord.com/api/v8/channels/{Vars.channelId}/messages/{best_card_id}/reactions/%E2%9D%A4%EF%B8%8F/%40me', headers=auth)
    else:
        print('Você não tem regates')

    if Vars.pokeRoll:
        print('\nTrying to roll Pokeslot')
        requests.post(url=url, headers=auth, data={'content': '$p'})
