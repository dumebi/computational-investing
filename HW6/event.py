import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas
from pylab import *
import copy
import QSTK.qstkstudy.EventProfiler as ep
from collections import defaultdict
import math
import csv


def find_events(ls_symbols, d_data):
    orders = []
    adjcloses = d_data['close']
    adjcloses = adjcloses.fillna(1.0)
    adjcloses = adjcloses.fillna(method='backfill')
    means = adjcloses.rolling(min_periods=20,window=20,center=False).mean()
    stdev = adjcloses.rolling(min_periods=20,window=20,center=False).std()
    upper_band = means + stdev
    lower_band = means - stdev
    std_output = (adjcloses - means) / stdev
    std_output = std_output.fillna(method='backfill')
    # prepare the date data
    ldt_timestamps = adjcloses.index
    print "Finding Events"
    # fill the event matrix
    for each_stock in ls_symbols:
        for i in range(1, len(ldt_timestamps) - 1):
            if std_output[each_stock].values[i] < -2.0 and std_output[each_stock].values[i - 1] >= -2.0 and \
                            std_output['SPY'].values[i] >= 1.1:
                buy_date = (ldt_timestamps[i].year, ldt_timestamps[i].month, ldt_timestamps[i].day)
                if (i + 5) <= (len(ldt_timestamps) - 1):
                    sell_date = (ldt_timestamps[i + 5].year, ldt_timestamps[i + 5].month, ldt_timestamps[i + 5].day)
                else:
                    sell_date = (ldt_timestamps[-1].year, ldt_timestamps[-1].month, ldt_timestamps[-1].day)
                orders.append((buy_date[0], buy_date[1], buy_date[2], each_stock, 'Buy', 100))
                orders.append((sell_date[0], sell_date[1], sell_date[2], each_stock, 'Sell', 100))
    return (orders)


# prepare the time data
startday = dt.datetime(2008, 1, 1)
endday = dt.datetime(2009, 12, 31)
timeofday = dt.timedelta(hours=16)
ldt_timestamps = du.getNYSEdays(startday, endday, timeofday)
dataobj = da.DataAccess('Yahoo')
ls_symbols = dataobj.get_symbols_from_list("sp5002012")
ls_symbols.append('SPY')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))
for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)
# call the find event function
order_list = find_events(ls_symbols, d_data)

with open("try.csv", "wb") as datafile:
    csv_writer = csv.writer(datafile)
    for each in order_list:
        csv_writer.writerow(each)