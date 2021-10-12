# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
from constants import *
import os


#bit docs
#https://ofek.dev/bit/guide/keys.html

# Load and set environment variables
load_dotenv('.env')
mnemonic=os.getenv("MNEMONIC")
#print(mnemonic)

# Import constants.py and necessary functions from bit and web3
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
from bit import *
from web3 import Web3
from eth_account import Account

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
 
 
# Create a function called `derive_wallets`
def derive_wallets(mnemonicPhrase, coin, numdrive=3):
    command = f'/Users/econ77/Workspaces/Blockchain-Tools/wallet/derive -g --mnemonic="{mnemonicPhrase}" --cols=path,address,privkey,pubkey --coin="{coin}" --numderive="{numdrive}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.

coins = {
    BTCTEST: derive_wallets(mnemonic, BTCTEST),
    ETH: derive_wallets(mnemonic, ETH),
   # BTC: derive_wallets(mnemonic, BTC)
    }
print(json.dumps(coins, indent=4, sort_keys=True))

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin):
    if coin == ETH:
        priv_key = coins[ETH][0]['privkey']
        return Account.privateKeyToAccount(priv_key)
    #elif coin == BTC:
    #    priv_key = coins[BTC][0]['privkey']
    #    return PrivateKey(priv_key)
    if coin == BTCTEST:
        priv_key = coins[BTCTEST][0]['privkey']
        return PrivateKeyTestnet(priv_key)

#accBTC = priv_key_to_account(BTC)
accETH = priv_key_to_account(ETH)   
accBTCTEST = priv_key_to_account(BTCTEST)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH:
        gas_estimate = w3.eth.estimate_gas(
            {"from": account.address, "to": to, "value": amount}
        )
        return {
            'from': account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gas_estimate,
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainId": w3.eth.chain_id
        }
    #elif coin == BTC:
    #    return PrivateKey.prepare_transaction(account.address, [(to,amount,BTC)])
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to,amount,BTCTEST)])





# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account,recipent, amount):
    tx = create_tx(coin, account,recipent, amount)
    signed = account.sign_transaction(tx)
    if coin == ETH:
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    #elif coin == BTC:
       # return NetworkAPI.broadcast_tx(signed)
    if coin == BTCTEST:
        return NetworkAPI.broadcast_tx_testnet(signed)

#send_tx(ETH, accETH, '0xa87601B8dbA7C17081E67eC68E9aB749Fd7e1d07', 1)
#send_tx(BTC, accBTC, '', 0.0000001)
send_tx(BTCTEST, accBTCTEST, '37NFX8KWAQbaodUG6pE1hNUH1dXgkpzbyZ', 0.000000001)
print(priv_key_to_account(BTCTEST, (coins[BTCTEST][0]['privkey'])).get_transactions()[0])
