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
CYAN = '\033[36m'
RESET = '\033[0m'

def check_claim_status(server_config):
    logging.info("Sending '$tu' command to Discord")
    bot = discum.Client(token=server_config['token'], log=False)
    bot.sendMessage(server_config['channelId'], "$tu")
    time.sleep(2)

    response = get_discord_messages(server_config)
    logging.info("Response received from Discord")

    remaining_claim_time, rolls_ready, rolls_available, can_claim = parse_response(response)
    
    logging.info(HIGHLIGHT + f"Claim status for server {server_config['serverId']}: Remaining claim time: {remaining_claim_time} minutes, Rolls ready: {rolls_ready}, Rolls available: {rolls_available}" + RESET)
    
    return remaining_claim_time, rolls_ready, rolls_available, can_claim

def get_discord_messages(server_config):
    logging.info("Fetching messages from Discord")
    url = f"https://discord.com/api/v8/channels/{server_config['channelId']}/messages"
    r = requests.get(url, headers={'authorization': server_config['token']})
    return json.loads(r.text)

def parse_response(response):
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
    if Texts.current_language['next_claim_reset'] in content:
        return parse_time_string(content, Texts.current_language['next_claim_reset'], True)

    if Texts.current_language['cant_claim_for_another'] in content:
        return parse_time_string(content, Texts.current_language['cant_claim_for_another'], False)

    return remaining_claim_time, can_claim

def parse_time_string(content, text_key, can_claim):
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
    if Texts.current_language['you_have_rolls_left'] in content and Texts.current_language['rolls_left'] in content:
        rolls_available = int(content.split(f"{Texts.current_language['you_have_rolls_left']} **")[1].split("**")[0].strip())

    logging.info(f"Extracted rolls available: {rolls_available}")
    return rolls_available

def simpleRoll(remaining_claim_time, rolls_available, kakera_threshold, can_claim, server_config):
    logging.info(f"Starting roll at {time.strftime('%H:%M - %d/%m/%y', time.localtime())} for server {server_config['serverId']}")
    
    rolled_cards = []
    bot = discum.Client(token=server_config['token'], log=False)

    instant_claim = False
    for i in range(rolls_available):
        rollCommand = get_roll_command(bot)
        logging.debug(f"Rolling card {i + 1} on server {server_config['serverId']}...")
        bot.triggerSlashCommand(botID, server_config['channelId'], server_config['serverId'], data=rollCommand)
        time.sleep(1.8)

        rolled_card, instant_claim  = analyze_card(i, server_config, bot, can_claim)
        rolled_cards.append(rolled_card)

    highest_power, best_card = analyze_rolled_cards(rolled_cards)
    
    logging.info(CYAN + f"Best card power: {highest_power}, Best card name: {best_card['name']} on server {server_config['serverId']}" + RESET)
    process_kakera_reaction(rolled_cards, server_config, bot)
    
    if can_claim:
        process_claim(highest_power, best_card, remaining_claim_time, kakera_threshold, server_config, bot, instant_claim)
    else:
        logging.info(RED + f"Cannot claim any cards at the moment on server {server_config['serverId']}" + RESET)

    if server_config['pokeRoll']:
        roll_poke_slot(server_config, bot)

def get_roll_command(bot):
    logging.debug("Fetching roll command from bot")
    return SlashCommander(bot.getSlashCommands(botID).json()).get([Vars.rollCommand])

def analyze_card(index, server_config, bot, can_claim):
    logging.debug(f"Analyzing rolled card {index + 1} for server {server_config['serverId']}")
    url = f"https://discord.com/api/v8/channels/{server_config['channelId']}/messages"
    r = requests.get(url, headers={'authorization': server_config['token']})
    jsonCard = json.loads(r.text)
    card_data = extract_card_data(jsonCard[0])

    card_name = card_data['name']
    card_power = card_data['power']
    claimed = '❤️' if 'footer' in jsonCard[0]['embeds'][0] and 'icon_url' in jsonCard[0]['embeds'][0]['footer'] else '🤍'
    is_claimed = claimed == '❤️'
    card_data['claimed'] = is_claimed

    logging.info(f"Card {index + 1} - {claimed} ---- Power: {card_power} - Name: {card_name} on server {server_config['serverId']}")

    instant_claim = False
    if card_power >= server_config['kakeraThresholdInstantClaim'] and not is_claimed and can_claim:
        logging.info(GREEN + f"Instantly claiming card {card_name} with power {card_power} on server {server_config['serverId']}" + RESET)
        claim_card(card_data['id'], server_config, bot)
        instant_claim = True 
    
    return card_data, instant_claim

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
        if card['claimed']:
            logging.info(f"Skipping card {card['name']} because it has already been claimed.")
            continue

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

def process_claim(highest_power, best_card, remaining_claim_time, kakera_threshold, server_config, bot, instant_claim):
    is_last_hour = remaining_claim_time <= 60
    logging.info(BLUE + f"Initiating claim process, is last hour {is_last_hour} for server {server_config['serverId']}" + RESET)

    if best_card is None or best_card['claimed'] or instant_claim:
        logging.info(RED + "No valid unclaimed cards available for claiming." + RESET)
        return
    
    if not is_last_hour and highest_power >= kakera_threshold:
        logging.info(GREEN + f"Claiming card {best_card['name']} with {highest_power} power on server {server_config['serverId']}" + RESET)
        claim_card(best_card['id'], server_config, bot)
    elif is_last_hour:
        logging.info(GREEN + f"Claiming best card {best_card['name']} with {highest_power} power in last hour on server {server_config['serverId']}" + RESET)
        claim_card(best_card['id'], server_config, bot)
    else:
        logging.info(RED + f"No cards above {kakera_threshold} kakera on server {server_config['serverId']}" + RESET)


def claim_card(card_id, server_config, bot):
    logging.debug(f"Claiming card with id: {card_id} on server {server_config['serverId']}")
    requests.put(f'https://discord.com/api/v8/channels/{server_config["channelId"]}/messages/{card_id}/reactions/%E2%9D%A4%EF%B8%8F/%40me', headers={'authorization': server_config['token']})

def roll_poke_slot(server_config, bot):
    logging.info(f"Rolling Pokeslot on server {server_config['serverId']}")
    url = f"https://discord.com/api/v8/channels/{server_config['channelId']}/messages"
    requests.post(url=url, headers={'authorization': server_config['token']}, data={'content': '$p'})

