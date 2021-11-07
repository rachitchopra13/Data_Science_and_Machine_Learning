import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np 
import json
import re 

tickers = {'TCS.NS','TATASTEEL.NS','TITAN.NS','TATACHEM.NS','TATAPOWER.NS','INDHOTEL.NS','TATACONSUM.NS','TATACOMM.NS','VOLTAS.NS','TRENT.NS',
           'TATASTLLP.NS','TATAINVEST.NS','TATAMETALI.NS','TATAELXSI.NS','NELCO.NS','TATACOFFEE.NS','TATAMOTORS.NS'
           }

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

financial_dir ={}


income_st_url = 'https://finance.yahoo.com/quote/'+'/financials?p='
balsheet_url =  'https://finance.yahoo.com/quote/'+'/balance-sheet?p='
cash_flow_url = 'https://finance.yahoo.com/quote/'+'/cash-flow?p='
stats_url = 'https://finance.yahoo.com/quote/'+'/key-statistics?p='

for ticker in tickers:
    ## getting balance sheet data for the  particular ticker
    ######################################## BALANCE SHEET ########## 
    url = 'https://finance.yahoo.com/quote/'+ticker+'/balance-sheet?p='+ticker
    print(url)
    
    response  = requests.get(url,headers= headers)
    print(response.status_code)
    soup = BeautifulSoup(response.text,'html.parser')
    
    pattern = re.compile(r'\s--\sData\s--\s')
    script = soup.find('script',text = pattern)
    
    script_data = script.contents[0]
    start = script_data.find('context')-2
    json_data = json.loads(script_data[start:-12])
    
   
    annual_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistory']['balanceSheetStatements']
    
    balance_sheet = []
    for s in annual_bs:
        statement = {}
        for key, value in s.items():
            try:
                statement[key]= value['raw']
            except TypeError:
                continue
            except KeyError:
                continue
            balance_sheet.append(statement)
    balance_sheet = balance_sheet[0]
    
    


############################## INCOME STATEMENT ##############################
    ## getting Income statement data
    annual_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistory']['incomeStatementHistory']
    
    url = 'https://finance.yahoo.com/quote/'+ticker+'/financials?p='+ticker
    print(url)
    
    response  = requests.get(url,headers= headers)
    print(response.status_code)
    soup = BeautifulSoup(response.text,'html.parser')
    
    pattern = re.compile(r'\s--\sData\s--\s')
    script = soup.find('script',text = pattern)
    
    script_data = script.contents[0]
    start = script_data.find('context')-2
    json_data = json.loads(script_data[start:-12])
    
    
    annual_stmt = []
    for s in annual_is:
        statement = {}
        for key, value in s.items():
            try:
                statement[key]= value['raw']
            except TypeError:
                continue
            except KeyError:
                continue
            annual_stmt.append(statement)
    annual_stmt = annual_stmt[0]




######################################### CASHFLOW STATEMENT ################
    annual_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistory']['cashflowStatements']
    url = 'https://finance.yahoo.com/quote/'+ticker+'/cash-flow?p='+ticker
    print(url)
    
    response  = requests.get(url,headers= headers)
    print(response.status_code)
    soup = BeautifulSoup(response.text,'html.parser')
    
    pattern = re.compile(r'\s--\sData\s--\s')
    script = soup.find('script',text = pattern)
    
    script_data = script.contents[0]
    start = script_data.find('context')-2
    json_data = json.loads(script_data[start:-12])
    
    
    cashflow_stmt = []
    for s in annual_cf:
        statement = {}
        for key, value in s.items():
            try:
                statement[key]= value['raw']
            except TypeError:
                continue
            except KeyError:
                continue
            cashflow_stmt.append(statement)
    cashflow_stmt = cashflow_stmt[0]
    del(cashflow_stmt['endDate'])
       


############################## stats  ##############################
    ## getting stats data
    
    url = "https://finance.yahoo.com/quote/"+ticker+"/key-statistics?p="+ticker
    
    print(url)
    
    response  = requests.get(url,headers= headers)
    print(response.status_code)
    soup = BeautifulSoup(response.text,'html.parser')
    
    pattern = re.compile(r'\s--\sData\s--\s')
    script = soup.find('script',text = pattern)
    
    script_data = script.contents[0]
    start = script_data.find('context')-2
    json_data = json.loads(script_data[start:-12])
    annual_stats = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['summaryDetail']
    Totaldebt = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['financialData']['totalDebt']['raw']
    Book_value =json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['defaultKeyStatistics']['bookValue']['raw']
    
    
    stat_stmt = []
    
    statement = {}
    for key, value in annual_stats.items():
        try:
            statement[key] = value['raw']
        except TypeError:
            continue
        except KeyError:
            continue
        stat_stmt.append(statement)
    stat_stmt = stat_stmt[0]
    stat_stmt['totalDebt'] = Totaldebt
    stat_stmt['bookValue'] = Book_value
    
    

    

    
################### To DataFrame  ############################################
    
    financial_dir[ticker] = dict(annual_stmt,**balance_sheet,**cashflow_stmt,**stat_stmt)
    data = pd.DataFrame(financial_dir)
    
################## Key Financial Metrics #####################################

final_stats_df = pd.DataFrame()
final_stats_df['EBIT'] = data.loc['ebit']
final_stats_df['TEV'] = data.loc['minorityInterest']+data.loc['marketCap']+data.loc['totalDebt']-data.loc['otherCurrentAssets']-data.loc['totalCurrentLiabilities']
final_stats_df['EarningYield'] = final_stats_df['EBIT']/final_stats_df['TEV']
final_stats_df["FCFYield"] = (data.loc["totalCashFromOperatingActivities"]-data.loc["capitalExpenditures"])/data.loc["marketCap"]
final_stats_df["ROC"]  = final_stats_df['EBIT']/(data.loc["propertyPlantEquipment"]+data.loc["otherCurrentAssets"]-data.loc["totalCurrentLiabilities"])
final_stats_df["BookToMkt"] = data.loc["bookValue"]/data.loc["marketCap"]
final_stats_df["DivYield"] = data.loc["dividendYield"]

print(final_stats_df)

################# finding value stocks based on Magic Formula
final_stats_val_df = final_stats_df.loc[tickers,:]
final_stats_val_df["CombRank"] = final_stats_val_df["EarningYield"].rank(ascending=False,na_option='bottom')+final_stats_val_df["ROC"].rank(ascending=False,na_option='bottom')
final_stats_val_df["MagicFormulaRank"] = final_stats_val_df["CombRank"].rank(method='first')
value_stocks = final_stats_val_df.sort_values("MagicFormulaRank").iloc[:,[2,4,8]]
print("------------------------------------------------")
print("Value stocks based on Greenblatt's Magic Formula")
print(value_stocks)


############### finding highest dividend yield stocks
high_dividend_stocks = final_stats_df.sort_values("DivYield",ascending=False).iloc[:,6]
print("------------------------------------------------")
print("Highest dividend paying stocks")
print(high_dividend_stocks)


# # Magic Formula & Dividend yield combined
final_stats_df["CombRank"] = final_stats_df["EarningYield"].rank(ascending=False,method='first') \
                              +final_stats_df["ROC"].rank(ascending=False,method='first')  \
                              +final_stats_df["DivYield"].rank(ascending=False,method='first')
final_stats_df["CombinedRank"] = final_stats_df["CombRank"].rank(method='first')
value_high_div_stocks = final_stats_df.sort_values("CombinedRank").iloc[:,[2,4,6,8]]
print("------------------------------------------------")
print("Magic Formula and Dividend Yield combined")
print(value_high_div_stocks)





















