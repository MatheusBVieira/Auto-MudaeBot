import discum
import json
import time
import requests
import Vars
import re
import logging
from discum.utils.slash import SlashCommander
from Texts import Texts

botID = '432610292342587392'  # ID do bot Mudae
HIGHLIGHT = '\033[93m\033[1m'
GREEN = '\033[32m'
RED = '\033[31m'
BLUE = '\033[34m'
RESET = '\033[0m'

def check_claim_status(server_config):
    """Executa o comando $tu e analisa o status do claim e rolls"""
    logging.info("Sending '$tu' command to Discord")
    bot = discum.Client(token=server_config['token'], log=False)
    bot.sendMessage(server_config['channelId'], "$tu")
    time.sleep(2)  # Aguardar resposta do bot

    response = get_discord_messages(server_config)
    logging.info("Response received from Discord")

    remaining_claim_time, rolls_ready, rolls_available, can_claim = parse_response(response)
    
    logging.info(HIGHLIGHT + f"Claim status for server {server_config['serverId']}: Remaining claim time: {remaining_claim_time} minutes, Rolls ready: {rolls_ready}, Rolls available: {rolls_available}" + RESET)
    
    return remaining_claim_time, rolls_ready, rolls_available, can_claim

def get_discord_messages(server_config):
    """Obtém as mensagens do canal do Discord"""
    logging.info("Fetching messages from Discord")
    url = f"https://discord.com/api/v8/channels/{server_config['channelId']}/messages"
    r = requests.get(url, headers={'authorization': server_config['token']})
    return json.loads(r.text)

def parse_response(response):
    """Analisa a resposta e extrai informações sobre tempo de claim e rolls"""
    remaining_claim_time = 0
    rolls_ready = 0
    rolls_available = 0
    can_claim = True
    
    logging.info("Parsing response for claim status and rolls")
    for message in response:
        if Texts.current_language['claim'] in message['content']:
            content = message['content']
            remaining_claim_time, can_claim = extract_claim_time(content, remaining_claim_time, can_claim)
            rolls_ready = extract_rolls_ready(content, rolls_ready)
            rolls_available = extract_rolls_available(content, rolls_available)

            logging.info(f"Extracted claim time: {remaining_claim_time}, Rolls ready: {rolls_ready}, Rolls available: {rolls_available}")
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
    
    logging.info(f"Parsed time string '{hours_minutes}' as {remaining_claim_time} minutes")
    return remaining_claim_time, can_claim

def extract_rolls_ready(content, rolls_ready):
    """Extrai o tempo de rolls da mensagem"""
    if Texts.current_language['next_rolls_reset'] in content:
        rolls_time_string = content.split(f"{Texts.current_language['next_rolls_reset']} **")[1]
        time_parts = rolls_time_string.split('min.')[0].strip()

        if 'h' in time_parts:
            hours_minutes = rolls_time_string.split("**")[0].strip()
            hours, minutes = map(int, re.findall(r'\d+', hours_minutes))
            rolls_ready = minutes
        else:
            rolls_ready = int(re.search(r'\d+', rolls_time_string).group())
    
    logging.info(f"Extracted rolls ready time: {rolls_ready} minutes")
    return rolls_ready

def extract_rolls_available(content, rolls_available):
    """Extrai o número de rolls disponíveis"""
    if Texts.current_language['you_have_rolls_left'] in content and Texts.current_language['rolls_left'] in content:
        rolls_available = int(content.split(f"{Texts.current_language['you_have_rolls_left']} **")[1].split("**")[0].strip())

    logging.info(f"Extracted rolls available: {rolls_available}")
    return rolls_available

def simpleRoll(remaining_claim_time, rolls_available, kakera_threshold, can_claim, server_config):
    logging.info(f"Starting roll at {time.strftime('%H:%M - %d/%m/%y', time.localtime())} for server {server_config['serverId']}")
    
    rolled_cards = []
    bot = discum.Client(token=server_config['token'], log=False)

    for i in range(rolls_available):
        rollCommand = get_roll_command(bot)
        logging.info(f"Rolling card {i + 1} on server {server_config['serverId']}...")
        bot.triggerSlashCommand(botID, server_config['channelId'], server_config['serverId'], data=rollCommand)
        time.sleep(1.8)

        rolled_card = analyze_card(i, server_config, bot)
        rolled_cards.append(rolled_card)

    highest_power, best_card = analyze_rolled_cards(rolled_cards)
    
    logging.info(f"Best card power: {highest_power}, Best card name: {best_card['name']} on server {server_config['serverId']}")
    process_kakera_reaction(rolled_cards, server_config, bot)
    
    if can_claim:
        process_claim(highest_power, best_card, remaining_claim_time, kakera_threshold, server_config, bot)
    else:
        logging.info(f"Cannot claim any cards at the moment on server {server_config['serverId']}")

    if server_config['pokeRoll']:
        roll_poke_slot(server_config, bot)

def get_roll_command(bot):
    logging.info("Fetching roll command from bot")
    return SlashCommander(bot.getSlashCommands(botID).json()).get([Vars.rollCommand])

def analyze_card(index, server_config, bot):
    logging.info(f"Analyzing rolled card {index + 1} for server {server_config['serverId']}")
    url = f"https://discord.com/api/v8/channels/{server_config['channelId']}/messages"
    r = requests.get(url, headers={'authorization': server_config['token']})
    jsonCard = json.loads(r.text)
    card_data = extract_card_data(jsonCard[0])

    # Log the details of the card
    card_name = card_data['name']
    card_power = card_data['power']
    claimed = '❤️' if 'footer' in jsonCard[0]['embeds'][0] and 'icon_url' in jsonCard[0]['embeds'][0]['footer'] else '🤍'
    logging.info(f"Card {index + 1} - {claimed} ---- Power: {card_power} - Name: {card_name} on server {server_config['serverId']}")
    
    return card_data

def extract_card_data(card):
    try:
        card_name = card['embeds'][0]['author']['name']
        card_series = card['embeds'][0]['description'].split('**')[0]
        card_power = int(card['embeds'][0]['description'].split('**')[1])
    except (IndexError, KeyError, ValueError):
        logging.error(f"Error extracting card data: {e}")
        card_name = 'null'
        card_series = 'null'
        card_power = 0
    return {'name': card_name, 'series': card_series, 'power': card_power, 'id': card['id'], 'components': card.get('components', [])}

def analyze_rolled_cards(rolled_cards):
    highest_power = 0
    best_card = None
    logging.info("Analyzing rolled cards for the best card")
    for card in rolled_cards:
        if card['power'] > highest_power:
            highest_power = card['power']
            best_card = card
    return highest_power, best_card

def process_kakera_reaction(rolled_cards, server_config, bot):
    logging.info("Processing kakera reactions")
    for card in rolled_cards:
        components = card.get('components', [])
        for component in components:
            if 'emoji' in component and component['emoji']['name'] in Vars.desiredKakeras:
                logging.info(f"Reacting to kakera emoji: {component['emoji']['name']} on card: {card['name']}")
                react_to_kakera(card['id'], component['custom_id'], server_config, bot)

def react_to_kakera(message_id, custom_id, server_config, bot):
    logging.info(f"Reacting to message {message_id} with custom_id {custom_id} on server {server_config['serverId']}")
    bot.click(botID, server_config['channelId'], server_config['serverId'], messageID=message_id, data={'component_type': 2, 'custom_id': custom_id})

def process_claim(highest_power, best_card, remaining_claim_time, kakera_threshold, server_config, bot):
    is_last_hour = remaining_claim_time <= 60
    logging.info(BLUE + f"Initiating claim process, is last hour {is_last_hour} for server {server_config['serverId']}" + RESET)
    if not is_last_hour and highest_power >= kakera_threshold:
        logging.info(GREEN + f"Claiming card {best_card['name']} with {highest_power} power on server {server_config['serverId']}" + RESET)
        claim_card(best_card['id'], server_config, bot)
    else:
        logging.info(RED + f"No cards above {kakera_threshold} kakera on server {server_config['serverId']}" + RESET)

    if is_last_hour:
        logging.info(GREEN + f"Claiming best card {best_card['name']} with {highest_power} power in last hour on server {server_config['serverId']}" + RESET)
        claim_card(best_card['id'], server_config, bot)

def claim_card(card_id, server_config, bot):
    logging.info(f"Claiming card with id: {card_id} on server {server_config['serverId']}")
    requests.put(f'https://discord.com/api/v8/channels/{server_config["channelId"]}/messages/{card_id}/reactions/%E2%9D%A4%EF%B8%8F/%40me', headers={'authorization': server_config['token']})

def roll_poke_slot(server_config, bot):
    logging.info(f"Rolling Pokeslot on server {server_config['serverId']}")
    url = f"https://discord.com/api/v8/channels/{server_config['channelId']}/messages"
    requests.post(url=url, headers={'authorization': server_config['token']}, data={'content': '$p'})

