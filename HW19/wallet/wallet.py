# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
from constants import BTC, BTCTEST, ETH
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

from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware



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
    ETH: derive_wallets(mnemonic, ETH)
   # BTC: derive_wallets(mnemonic, BTC)
   }
#print(json.dumps(coins, indent=4, sort_keys=True))

btctest_priv_key = coins[BTCTEST][0]['privkey']
eth_priv_key = coins[ETH][0]['privkey']

## Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    #elif coin == BTC:
    #    priv_key = coins[BTC][0]['privkey']
    #    return PrivateKey(priv_key)
    if coin == BTCTEST:
       return PrivateKeyTestnet(priv_key)

#accBTC = priv_key_to_account(BTC)
accETH = priv_key_to_account(ETH, eth_priv_key)   
accBTCTEST = priv_key_to_account(BTCTEST, btctest_priv_key)
#print(accBTCTEST)


## Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
   if coin == ETH:
       gas_estimate = Web3.eth.estimate_gas(
           {"from": account.address, "to": to, "value": amount}
       )
       return {
           'from': account.address,
           "to": to,
           "value": amount,
           "gasPrice": Web3.eth.gasPrice,
           "gas": gas_estimate,
           "nonce": Web3.eth.getTransactionCount(account.address),
           "chainId": Web3.eth.chain_id
       }
   #elif coin == BTC:
   #    return PrivateKey.prepare_transaction(account.address, [(to,amount,coin)])
   else:
       return PrivateKeyTestnet.prepare_transaction(account.address, [(to,amount,BTC)])
print(accBTCTEST.address)
print(accETH.address)
tx_test = create_tx(BTCTEST, accBTCTEST,'2N83F3qNp5A13EtUxhUpHLzYGMZZqGkDwtS', 0.000000001)
print(tx_test)


# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, recipent, amount):
    tx = create_tx(coin, account, recipent, amount)
    signed = account.sign_transaction(tx)
    if coin == ETH:
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    #elif coin == BTC:
       # return NetworkAPI.broadcast_tx(signed)
    if coin == BTCTEST:
        return NetworkAPI.broadcast_tx_testnet(signed)

#send_tx(ETH, accETH, '0xa87601B8dbA7C17081E67eC68E9aB749Fd7e1d07', 1)
#send_tx(BTC, accBTC, '', 0.0000001)

send_tx(BTCTEST, accBTCTEST, '2N83F3qNp5A13EtUxhUpHLzYGMZZqGkDwtS', 0.000000001)
print(priv_key_to_account(BTCTEST, (coins[BTCTEST][0]['privkey'])).get_transactions()[0])
