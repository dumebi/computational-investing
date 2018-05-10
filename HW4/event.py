import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import copy
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import QSTK.qstkstudy.EventProfiler as ep
from collections import defaultdict
import math

def update(cash,num,price,stock_index):
    cash-=num*price
    share[stock_index]=share[stock_index]+num
    #print(cash)
    #print(share)
    return(cash,share[stock_index])

def find_events(ls_symbols, d_data):
    orders=[]
    df_close = d_data['actual_close']
    ldt_timestamps = df_close.index
    print "Finding Events"
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN
    for each_stock in ls_symbols:
        for i in range(1,len(ldt_timestamps)-1):
            if df_close[each_stock].ix[ldt_timestamps[i]]<10.0 and df_close[each_stock].ix[ldt_timestamps[i-1]]>=10.0:
                buy_date=(ldt_timestamps[i].year,ldt_timestamps[i].month,ldt_timestamps[i].day)
                if (i+5)<=(len(ldt_timestamps)-1):
                    sell_date=(ldt_timestamps[i+5].year,ldt_timestamps[i+5].month,ldt_timestamps[i+5].day)
                else:
                    sell_date=(ldt_timestamps[-1].year,ldt_timestamps[-1].month,ldt_timestamps[-1].day)
                orders.append((buy_date[0],buy_date[1],buy_date[2],each_stock,'Buy',100))
                orders.append((sell_date[0],sell_date[1],sell_date[2],each_stock,'Sell',100))
    return(orders)

#get the sp500 data
dt_start = dt.datetime(2008, 1, 1)
dt_end = dt.datetime(2009, 12, 31)
dt_timeofday = dt.timedelta(hours=16)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
dataobj=da.DataAccess('Yahoo')
symbols=dataobj.get_symbols_from_list("sp5002012")
symbols.append('SPY')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))
for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
        d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
order_list = find_events(symbols, d_data)
for each in order_list:
    print(each)
#from the order list to generate the order dictionary
orders= {}
orders = defaultdict(list)  #dict's element is list
symbols_orders=[]       #the stock symbols traded in orders
for each in order_list:
    orders[(int(each[0]), int(each[1]), int(each[2]))].append((each[3], each[4], int(each[5])))
    symbols_orders.append(each[3])
date=orders.keys()
date.sort()
symbols_orders=list(set(symbols_orders))
#print(symbols_orders)
#get the actual close price for the stocks inside orders
ldf_data = dataobj.get_data(ldt_timestamps, symbols_orders, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))
na_price = d_data['close'].values
#print(len(na_price),len(na_price[0]),na_price)

# shares of each stock in hand
share=[]
for j in range(0,len(symbols_orders)):
    share.append(0)
#deal with the orders
cash=50000
value=[]
for i,t in enumerate(ldt_timestamps):
    port_value=0
    if (t.year,t.month,t.day) in date:
        current_order=orders[(t.year,t.month,t.day)]
        #print(current_order)
        for each_order in current_order:
            sym=each_order[0]
            sym_index=symbols_orders.index(sym)
            action=each_order[1]
            num=each_order[2]
            if action=='Sell':
                num=-num
            (cash,share[sym_index])=update(cash,num,na_price[i][sym_index],sym_index)
    for k in range(0,len(symbols_orders)):
        port_value+=share[k]*na_price[i][k]
    value.append(cash+port_value)
    print(t.year,t.month,t.day,cash+port_value)
#print(value)
k=2
daire_port=[0]
while k<len(value)-2:
    daire_port.append(value[k]/value[k-1]-1)
    k=k+1
daire_port=np.array(daire_port)
average=np.average(daire_port)
stdev=np.std(daire_port)
sharpe=math.sqrt(252)*average/stdev
print "Sharpe Ratio of Portfolio:",sharpe
total_re=value[-1]/value[0]
print "Total Return of Portfolio:",total_re