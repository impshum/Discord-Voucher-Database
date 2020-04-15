## Discord Voucher Database

Stores and supplies stored cinema vouchers over Discord.

### Instructions

-   Install requirements `pip install -r requirements.txt`
-   Create Discord app and bot: https://discordpy.readthedocs.io/en/latest/discord.html
-   Edit conf.ini with your Discord token
-   Put all the voucher codes in their relative txt file in the data directory
-   Run it `python run.py`

### Help

/help - Show help  
/stats - Show used/unused count
/readall - Read all in database add a number to limit results

Start the process with /v  

1b = 1 x bundle  
1t = 1 x ticket  
1p = 1 x popcorn  
1d = 1 x drink  

Examples

    /v 2t 1p 2d
    /readall3

### Tip

BTC - 1AYSiE7mhR9XshtS4mU2rRoAGxN8wSo4tK
