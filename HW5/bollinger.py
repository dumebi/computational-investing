import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas
from pylab import *

#
# Prepare to read the data
#
symbols = ["AAPL","GOOG","IBM","MSFT"]
startday = dt.datetime(2010,1,1)
endday = dt.datetime(2010,12,31)
timeofday=dt.timedelta(hours=16)
timestamps = du.getNYSEdays(startday,endday,timeofday)

dataobj = da.DataAccess('Yahoo')
#voldata = dataobj.get_data(timestamps, symbols, "volume")
adjcloses = dataobj.get_data(timestamps, symbols, "close")
#actualclose = dataobj.get_data(timestamps, symbols, "actual_close")
#adjcloses = adjcloses.fillna()
adjcloses = adjcloses.fillna(method='backfill')

means = pandas.rolling_mean(adjcloses,20,min_periods=20)
stdev = pandas.rolling_std(adjcloses,20,min_periods=20)
upper_band=means+stdev
lower_band=means-stdev
# Plot the prices
for symtoplot in symbols:
    plt.clf()
#symtoplot = 'GOOG'
    plot(adjcloses.index,adjcloses[symtoplot].values,label=symtoplot)
    plot(adjcloses.index,means[symtoplot].values)
    plot(adjcloses.index,upper_band[symtoplot].values)
    plot(adjcloses.index,lower_band[symtoplot].values)
    plt.legend([symtoplot,'Moving Avg.','Upper Band','Lower Band'],'lower left')
    plt.ylabel('Adjusted Close')
    filename=symtoplot+".png"
    savefig(filename, format='png')

#standard output
std_output=(adjcloses-means)/stdev
for i in range(0,len(timestamps)):
    print(timestamps[i].year,timestamps[i].month,timestamps[i].day,std_output.values[i])
