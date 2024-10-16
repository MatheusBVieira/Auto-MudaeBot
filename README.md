
# Mudae AutoRoll AutoClaim AutoReact 2024  
### by GDiazFentanes

## Introduction  
Auto Rolling, Auto Claiming, and Auto Reacting to claim waifus, kakeras, or husbandos from Mudae automatically every hour. Now with an enhanced rolling and decision system based on kakera values. These files allow you to use the Mudae Discord Bot 24/7 without human input. You only need basic knowledge of Discord and Python to use it.

## Features  
- **Auto Roll** every hour with the configured command.
- **Auto Claim** cards from desired series or based on kakera criteria.
- **Auto React** only to the kakeras you prefer.
- **Kakera-based decision making**: Evaluates cards during regular time and, in the last hour before reset, prioritizes the card with the highest value.
- **Automatic claim time checking**: Uses the `$tu` command to get the available time for rolls and the exact moment for claim.
- **Roll execution in 3-hour intervals**, adjusting the claim strategy as time progresses.
- **Kakera Priority**: Defines minimum kakera values to claim automatically in the first two hours and, in the final hour, prioritizes the highest value card.
- **BONUS** - Always uses slash commands to benefit from the native kakera boost (+10%).

## Files  
This repository contains 3 different files:

| File Name | File Purpose | Notes |
| ------ | ------ | ------ |
| Vars.py | Stores configurable bot variables | Edit as needed |
| Bot.py | Launches the bot from this file | Run to start the bot |
| Function.py | Contains the main bot functions | No action needed |

## Requirements  
This bot requires the following libraries to function properly:

- [Discum](https://pypi.org/project/discum/) for message management.
- [Schedule](https://pypi.org/project/schedule/) to ensure it runs at the scheduled time.

Install with:
```bash
pip install discum
pip install schedule
```

## How to set up / use  
##### Packages  
Ensure Python 3 is installed, along with the Discum and Schedule libraries. If you're unsure, check here → [How to install Python packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)

##### Variables (Vars)  
Open `Vars.py` and configure it as follows:

**Mandatory variables**:
+ `token` - The Discord token for the account you want to bot with → [How to get your Discord token](https://www.androidauthority.com/get-discord-token-3149920/)
+ `channelId` - ID of the channel where commands will be executed → [How to get the channel ID](https://docs.statbot.net/docs/faq/general/how-find-id/)  
+ `serverId` - ID of the server where the bot will operate → [How to get the server ID](https://docs.statbot.net/docs/faq/general/how-find-id/)  

**Optional variables**:
+ `rollCommand` - Command to use for rolling (e.g., mx, wa, hx)
+ `desiredKakeras` - Preferred kakera types (Case-sensitive)
+ `kakeraThresholdNormal` - Minimum kakera value during regular hours
+ `kakeraThresholdFinalHour` - Minimum kakera value during the final hour before reset
+ `pokeRoll` - Whether the bot should also roll Pokeslot (True/False)
+ `repeatMinute` - Specific minute when the bot should roll (between 00 and 59)

##### Example of configuration
```python
token = 'your_token_here'
channelId = 'channel_id_here'
serverId = 'server_id_here'
rollCommand = 'wa'
desiredKakeras = ['kakeraP', 'kakeraY', 'kakeraO']
kakeraThresholdNormal = 250
kakeraThresholdFinalHour = 0
pokeRoll = True
```

##### Execution  
Once configured, execute the `Bot.py` file. It will roll the command and react to cards/kakeras automatically at the scheduled times.

## Possible Errors  
- Mudae has no read/write permissions in the selected channel.
- Your Discord token has changed.
- Button settings for Mudae are incorrect.
- Series and kakera names are case-sensitive.

## Advanced Bot Features  
The advanced version of the bot includes:

- **Desired Characters**: AutoClaim specific characters with priority.
- **Optimized Kakera reaction**: An algorithm to prioritize higher-value kakeras.
- **Optimized Claiming**: Claims the highest-value card if no preferred series match.
- **$dk command optimization**: Uses the DK command efficiently to maximize kakera gains.
- **$rt command optimization**: Uses the $rt command if a claim is not available.
- **Multi-Bot**: Support for multiple Discord accounts to maximize efficiency.
