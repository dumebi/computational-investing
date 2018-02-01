import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
from collections import defaultdict
import math

def update(cash,num,price,stock_index):
    cash-=num*price
    share[stock_index]=share[stock_index]+num
    #print(cash)
    #print(share)
    return(cash,share[stock_index])

#read the orders from the csv file
orders= {}
orders = defaultdict(list)  #dict's element is list
symbols=[]
with open('try.csv','rb') as csvfile:
    for each in csvfile:
        order=each.split(",")
        orders[(int(order[0]), int(order[1]), int(order[2]))].append((order[3], order[4], int(order[5])))
        symbols.append(order[3])
date=orders.keys()
date.sort()
start=date[0]
end=(date[-1][0],date[-1][1],date[-1][2]+1)
symbols=list(set(symbols))
#print(orders)
#print(date)

#get date series and price
dt_start = dt.datetime(int(start[0]),int(start[1]),int(start[2]))
dt_end = dt.datetime(int(end[0]),int(end[1]),int(end[2]))

dt_timeofday = dt.timedelta(hours=16)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
c_dataobj = da.DataAccess('Yahoo')
ls_keys = ['close']
ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))
for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
    d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)

na_price = d_data['close'].values


#scan the orders and update the cash and calculate the portfolio value
cash=100000   #the initial value of cash
share=[]
for j in range(0,len(symbols)):
    share.append(0)
value=[]
for i,t in enumerate(ldt_timestamps):
    port_value=0
    if (t.year,t.month,t.day) in date:
        current_order=orders[(t.year,t.month,t.day)]
        #print(current_order)
        for each_order in current_order:
            sym=each_order[0]
            sym_index=symbols.index(sym)
            action=each_order[1]
            num=each_order[2]
            if action=='Sell':
                num=-num
            (cash,share[sym_index])=update(cash,num,na_price[i][sym_index],sym_index)
    #print(t,cash+share[0]*na_price[i][0]+share[1]*na_price[i][1]+share[2]*na_price[i][2]+share[3]*na_price[i][3])
    for k in range(0,len(symbols)):
        port_value+=share[k]*na_price[i][k]
    value.append(cash+port_value)
    #print(t.year,t.month,t.day,cash+port_value)

k=1
daire_port=[0]
while k<len(value):
    daire_port.append(value[k]/value[k-1]-1)
    k=k+1
#print(daire_port)
print(len(value),len(daire_port))
daire_port=np.array(daire_port)
average=np.average(daire_port)
stdev=np.std(daire_port)
print("average,stdev",average,stdev)
sharpe=math.sqrt(252)*average/stdev
print "Sharpe Ratio:",sharpe
total_re=value[-1]/value[0]
print("Total Return:"),total_re