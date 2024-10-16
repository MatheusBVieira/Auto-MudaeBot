import discum
import json
import time
import requests
import Vars
import re
from discum.utils.slash import SlashCommander
from Texts import Texts

botID = '432610292342587392'  # ID do bot Mudae
auth = {'authorization': Vars.token}
bot = discum.Client(token=Vars.token, log=False)
url = f'https://discord.com/api/v8/channels/{Vars.channelId}/messages'

def check_claim_status():
    """Executa o comando $tu e analisa o status do claim e rolls"""
    bot.sendMessage(Vars.channelId, "$tu")
    time.sleep(2)  # Aguardar resposta do bot

    response = get_discord_messages()
    remaining_claim_time, rolls_ready, rolls_available, can_claim = parse_response(response)
    
    return remaining_claim_time, rolls_ready, rolls_available, can_claim

def get_discord_messages():
    """Obtém as mensagens do canal do Discord"""
    r = requests.get(f"https://discord.com/api/v8/channels/{Vars.channelId}/messages", headers={'authorization': Vars.token})
    return json.loads(r.text)

def parse_response(response):
    """Analisa a resposta e extrai informações sobre tempo de claim e rolls"""
    remaining_claim_time = 0
    rolls_ready = 0
    rolls_available = 0
    can_claim = True
    
    for message in response:
        if 'claim' in message['content']:
            content = message['content']
            remaining_claim_time, can_claim = extract_claim_time(content, remaining_claim_time, can_claim)
            rolls_ready = extract_rolls_ready(content, rolls_ready)
            rolls_available = extract_rolls_available(content, rolls_available)

            break
    
    return remaining_claim_time, rolls_ready, rolls_available, can_claim

def extract_claim_time(content, remaining_claim_time, can_claim):
    """Extrai o tempo de claim da mensagem"""
    if Texts.current_language['next_claim_reset'] in content:
        return parse_time_string(content, Texts.current_language['next_claim_reset'], True)

    if Texts.current_language['cant_claim_for_another'] in content:
        return parse_time_string(content, Texts.current_language['cant_claim_for_another'], False)

    return remaining_claim_time, can_claim

def parse_time_string(content, text_key, can_claim):
    """Converte o tempo de texto para minutos"""
    claim_time_string = content.split(f"{text_key} **")[1]
    hours_minutes = claim_time_string.split("**")[0].strip()

    if 'h' in hours_minutes:
        hours, minutes = map(int, re.findall(r'\d+', hours_minutes))
        remaining_claim_time = hours * 60 + minutes
    else:
        minutes = int(re.search(r'\d+', hours_minutes).group())
        remaining_claim_time = minutes
    
    return remaining_claim_time, can_claim

def extract_rolls_ready(content, rolls_ready):
    """Extrai o tempo de rolls da mensagem"""
    if Texts.current_language['next_rolls_reset'] in content:
        rolls_time_string = content.split(f"{Texts.current_language['next_rolls_reset']} **")[1]
        rolls_ready = int(re.search(r'\d+', rolls_time_string).group())
    
    return rolls_ready

def extract_rolls_available(content, rolls_available):
    """Extrai o número de rolls disponíveis"""
    if Texts.current_language['you_have_rolls_left'] in content and Texts.current_language['rolls_left'] in content:
        rolls_available = int(content.split(f"{Texts.current_language['you_have_rolls_left']} **")[1].split("**")[0].strip())

    return rolls_available

def simpleRoll(remaining_claim_time, rolls_available, kakera_threshold, can_claim):
    print(time.strftime("Rolling at %H:%M - %d/%m/%y", time.localtime()))
    rolled_cards = []

    for i in range(rolls_available):
        rollCommand = get_roll_command()
        bot.triggerSlashCommand(botID, Vars.channelId, Vars.serverId, data=rollCommand)
        time.sleep(1.8)

        rolled_card = analyze_card()
        rolled_cards.append(rolled_card)
        break  # Interrompe o loop após adicionar a primeira carta

    highest_power, best_card = analyze_rolled_cards(rolled_cards)
    
    process_kakera_reaction(rolled_cards)
    
    if can_claim:
        process_claim(highest_power, best_card, remaining_claim_time, kakera_threshold)
    else:
        print('Você não tem regates')

    if Vars.pokeRoll:
        roll_poke_slot()

def get_roll_command():
    return SlashCommander(bot.getSlashCommands(botID).json()).get([Vars.rollCommand])

def analyze_card():
    r = requests.get(url, headers=auth)
    jsonCard = json.loads(r.text)
    card_data = extract_card_data(jsonCard[0])
    return card_data

def extract_card_data(card):
    try:
        card_name = card['embeds'][0]['author']['name']
        card_series = card['embeds'][0]['description'].split('**')[0]
        card_power = int(card['embeds'][0]['description'].split('**')[1])
    except (IndexError, KeyError, ValueError):
        card_name = 'null'
        card_series = 'null'
        card_power = 0
    return {'name': card_name, 'series': card_series, 'power': card_power, 'id': card['id'], 'components': card.get('components', [])}

def analyze_rolled_cards(rolled_cards):
    highest_power = 0
    best_card = None
    for card in rolled_cards:
        if card['power'] > highest_power:
            highest_power = card['power']
            best_card = card
    return highest_power, best_card

def process_kakera_reaction(rolled_cards):
    for card in rolled_cards:
        components = card.get('components', [])
        for component in components:
            if 'emoji' in component and component['emoji']['name'] in Vars.desiredKakeras:
                react_to_kakera(card['id'], component['custom_id'])

def react_to_kakera(message_id, custom_id):
    bot.click(botID, Vars.channelId, Vars.serverId, messageID=message_id, data={'component_type': 2, 'custom_id': custom_id})

def process_claim(highest_power, best_card, remaining_claim_time, kakera_threshold):
    is_last_hour = remaining_claim_time <= 60
    if not is_last_hour and highest_power >= kakera_threshold:
        print(f'Trying to claim {best_card["name"]} with {highest_power} power')
        claim_card(best_card['id'])
    elif is_last_hour:
        print(f'Claiming best card {best_card["name"]} with {highest_power} power')
        claim_card(best_card['id'])

def claim_card(card_id):
    requests.put(f'https://discord.com/api/v8/channels/{Vars.channelId}/messages/{card_id}/reactions/%E2%9D%A4%EF%B8%8F/%40me', headers=auth)

def roll_poke_slot():
    print('\nTrying to roll Pokeslot')
    requests.post(url=url, headers=auth, data={'content': '$p'})

