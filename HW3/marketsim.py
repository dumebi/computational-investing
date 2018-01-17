import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import csv
import sys
import time
from datetime import date

# we will create a MARKET SIMULATOR that accepts trading orders (buy and/or sell stocks)
# and keeps track of the value of the portfolio containing all the equities
# using the values of the stocks in historical data
# hw_analyze.py will then ANALYZE the performance of that portfolio

# the market simulator is used if you have a trading strategy containing
# executed trades. The simulator simulates those trades by executing them
# and computes the Sharpe Ratio, Standard Deviation,
# Average Daily Return of Fund, and Total/Cumulative Return of your strategy
# in order to measure the performance of that strategy

# details at http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_3

dates = []
symbols = []
# order_list=[]

starting_cash = float(sys.argv[1])
order_file = sys.argv[2]
out_file = sys.argv[3]

# step1: read in csv file and remove duplicates
# see marketsim-guidelines.pdf
reader = csv.reader(open(order_file, 'rU'), delimiter=',')
for row in reader:
    print row
    # ex: 2008, 12, 3, AAPL, BUY, 130
    dates.append(dt.datetime(int(row[0]), int(row[1]), int(row[2])))
    # need int, otherwise get "TypeError: an integer is required"
    symbols.append(row[3])

# order_list.sort(['date'])

# remove duplicates
# set(listWithDuplicates) is an unordered collection without duplicates
# so it removes the duplicates in listWithDuplicates
uniqueDates = list(set(dates))
uniqueSymbols = list(set(symbols))

# step 2 - read the data like in previous HW and tutorials
sortedDates = sorted(uniqueDates)
dt_start = sortedDates[0]
# End date should be offset-ed by 1 day to
# read the close for the last date. - see marketsim-guidelines.pdf
dt_end = sortedDates[-1] + dt.timedelta(days=1)

dataobj = da.DataAccess('Yahoo')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

ldf_data = dataobj.get_data(ldt_timestamps, uniqueSymbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

# step 3: create dataframe that contains trade matrix
# see marketsim-guidelines.pdf
df_trade = np.zeros((len(ldt_timestamps), len(uniqueSymbols)))
df_trade = pd.DataFrame(df_trade, index=[ldt_timestamps], columns=uniqueSymbols)

# iterate orders file and fill the number of shares for that
# symbol and date to create trade matrix


reader = csv.reader(open(order_file, 'rU'), delimiter=',')
for orderrow in reader:
    order_date = dt.datetime(int(orderrow[0]), int(orderrow[1]), int(orderrow[2])).date()
    print 'check orderrow', orderrow
    for index, row in df_trade.iterrows():
        if order_date == index.date():
            print 'orderdate is', order_date, 'index is', index
            if orderrow[4] == 'Buy':
                print 'buy'
                df_trade.set_value(index, orderrow[3], float(orderrow[5]))
                # df_trade.ix[index][orderrow[3]] += float(orderrow[5])
                # print ts_cash[index]
            elif orderrow[4] == "Sell":
                print 'sell'
                # df_trade.ix[index][orderrow[3]] -= float(orderrow[5])
                df_trade.set_value(index, orderrow[3], -float(orderrow[5]))
print df_trade

# step4: create timeseries containing cash values, all values are 0 initially
ts_cash = pd.Series(0.0, index=ldt_timestamps)
ts_cash[0] = starting_cash
# for each order in trade matrix, subtract the cash used in that trade
for index, row in df_trade.iterrows():
    ts_cash[index] -= np.dot(row.values.astype(float), d_data['close'].ix[index])

# print 'df_trade',df_trade.head()
# step5:
# append '_CASH' into the price date
df_close = d_data['close']
df_close['_CASH'] = 1.0

# append cash time series into the trade matrix
df_trade['_CASH'] = ts_cash

# convert to holding matrix
df_holding = df_trade.cumsum()
# df_trade = df_trade.cumsum(axis=1)
# axis=1 means sum over columns
# see http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.cumsum.html

# dot product on price (df_close) and holding/trade matrix (df_trade) to
# calculate portfolio on each date
ts_fund = np.zeros((len(ldt_timestamps), 1))
# ts_fund = pd.DataFrame(ts_fund, index=ldt_timestamps, columns='portfolio value')

ts_fund = df_holding.mul(df_close, axis='columns', fill_value=0).sum(axis=1)
# better to avoid iterating over rows unless necessary
# and try to use pandas' vectorized operations
# for index, row in df_trade.iterrows():
#        portfolio_value = np.dot(row.values.astype(float), df_close.ix[index].values)
#        ts_fund[index] = portfolio_value

# write this to csv
writer = csv.writer(open(out_file, 'wb'), delimiter=',')
for row_index in ts_fund.index:
    row_to_enter = [row_index.year, row_index.month, row_index.day, ts_fund[row_index]]
    writer.writerow(row_to_enter)