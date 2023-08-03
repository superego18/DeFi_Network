import pandas as pd
import re
import json
import requests

# transform matrix
ch = pd.read_csv("data/chains.csv")
list_ = ch['Date']
ch = ch.transpose()
ch.drop(['Timestamp'], axis=0, inplace=True)
ch.columns = list_
ch_ = ch[1:]
ch = ch_.reset_index()
# make chains list
ch_list = ch["index"]
ch_list = ch_list.tolist()
for i in range(len(ch_list)):
    ch_list[i] = ch_list[i].replace(" ","%20")
# make url list
add_list = []
for i in range(len(ch_list)):
    add_list.append(
        "https://defillama.com/_next/data/FzgqchTXLOEvMRf0CUivw/chain/"
        +str(ch_list[i])+".json?chain="+str(ch_list[i])
        )

# crawling
chain_list_result = []
for i in add_list:
    r = requests.get(i)
    chain = r.json()
    
    for j in range(len(chain['pageProps']['protocolsList'])):
        if 'subRows' in chain['pageProps']['protocolsList'][j].keys():
            for t in range(len(chain['pageProps']['protocolsList'][j]['subRows'])):
                chain_list_result.append(
                {
                    'chain' : chain['pageProps']['chain'],
                    'protocol': chain['pageProps']['protocolsList'][j]['subRows'][t]['name'],
                    'protocol_category': chain['pageProps']['protocolsList'][j]['subRows'][t]['category'],
                    'protocol_chains': chain['pageProps']['protocolsList'][j]['subRows'][t]['chains'],
                    'protocol_mcaptvl': chain['pageProps']['protocolsList'][j]['subRows'][t]['mcaptvl'],
                    'protocol_tvl': chain['pageProps']['protocolsList'][j]['subRows'][t]['tvl'],
                    'protocol_mcap': chain['pageProps']['protocolsList'][j]['subRows'][t]['mcap'],
                    'protocol_strikeTvl': chain['pageProps']['protocolsList'][j]['subRows'][t]['strikeTvl']


                }
                )
        else:
            chain_list_result.append(
            {
                'chain' : chain['pageProps']['chain'],
                'protocol': chain['pageProps']['protocolsList'][j]['name'],
                'protocol_category': chain['pageProps']['protocolsList'][j]['category'],
                'protocol_chains': chain['pageProps']['protocolsList'][j]['chains'],
                'protocol_mcaptvl': chain['pageProps']['protocolsList'][j]['mcaptvl'],
                'protocol_tvl': chain['pageProps']['protocolsList'][j]['tvl'],
                'protocol_mcap': chain['pageProps']['protocolsList'][j]['mcap'],
                'protocol_strikeTvl': chain['pageProps']['protocolsList'][j]['strikeTvl']


            }
            )   

df = pd.DataFrame(chain_list_result)

# add (C) to chain name

df["chain"] = "(C)" + df["chain"] 

df.to_csv("data/chain_data_v5.csv")