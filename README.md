# **Disclaimer: I am not liable for your losses or wrong transaction caused by this script. If you use it, you are on your own!**

# Kraken Automation
 Simple automation for DCA on kraken.com

## Prerequisites
- Python 3.9 or later
- package `requests` needs to be installed: `pip install requests`
- An account on kraken.com
- A sufficient amount of funds on your kraken.com account
- An API-Key of your kraken.com account with the following permissions
  - Query Funds
  - Create & Modify Orders
- 2FA for the API-Key set to password
- Setup the following files in your home directory
  - `.kraken_key` with content:
    ```noformat
    keykeykeykeykeykeykeykeykeykey
    secretsecretsecretsecretsecretsecretsecretsecret
    ```
  - `.kraken_otp` with content:
    ```noformat
    passwordpasswordpasswordpasswordpassword
    ```

## Configure buying amounts
Edit the `orders` list in kraken_dca.py. The format is a dictonary with `pair` and `amount`. The pair name kan be found in `https://api.kraken.com/0/public/AssetPairs`. For example to buy 50€ worth of BTC you need `pair` `XXBTZEUR` and `amount` of `50.0`. In the below example 50€ of each BTC and ETH are bought.
```python
    orders: List[OrderDict] = [
        {"pair": "XXBTZEUR", "amount": 50.0},  # buy 50 € worth of BTC
        {"pair": "XETHZEUR", "amount": 50.0},  # buy 50 € worth of ETH
    ]
```

## Actually execute transaction
Remove the line `"validate": "true"` in the `_buy` function in `kraken_dca.py`

## How to make this into a DCA script:
Schedule in crontab: 
- Edit crontab
  `crontab -e`
- To execute the script every first of the month at 00:00 system insert the following line and replace `/path/to` with the actual path.
  `0 0 1 * * python3.9 /path/to/kraken_automation/kraken_dca.py`

## Troubleshooting:
### General:
First, add `"validate": "true"` flag in the `_buy` function in `kraken_dca.py`
Execute the script manually. Stdout contains all information.
### Crontab:
The log is available in the `cwd` i.e. where kraken_dca.py is located