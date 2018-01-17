from __future__ import division
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


# we will ANALYZE the performance of the portfolio used in the MARKET SIMULATOR

# the market simulator is used if you have a trading strategy containing
# executed trades. The simulator simulates those trades by executing them
# and "hw3_analyze.py" computes the Sharpe Ratio, Standard Deviation,
# Average Daily Return of Fund, and Total/Cumulative Return of your strategy
# in order to measure the performance of that strategy

def analyze(portfolio_file, benchmark_symbol):
    dates = []
    portfolio_values = []

    # portfolio_file = sys.argv[1]
    # benchmark_symbol = sys.argv[2]

    # read in values.csv
    reader = csv.reader(open(portfolio_file, 'rU'), delimiter=',')
    for order in reader:
        dates.append(dt.datetime(int(order[0]), int(order[1]), int(order[2])))
        portfolio_values.append(float(order[3]))

    dt_start = dates[0]
    # End date should be offset-ed by 1 day to
    # read the close for the last date. - see marketsim-guidelines.pdf
    dt_end = dates[-1] + dt.timedelta(days=1)
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, benchmark_symbol, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # remove NAN from price data
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    na_price_benchmark = d_data['close'].values
    # see above for meaning of these lines

    # convert list to array
    portfolio_values = np.array(portfolio_values)

    na_normalized_price_portfolio = portfolio_values
    na_normalized_price_benchmark = na_price_benchmark / na_price_benchmark[0, :]

    # if ls_symbols=['AAPL', 'GLD', 'GOOG', 'XOM' then
    # na_price[0:50,3]) price for GOOG for 50 days
    # na_price[0:50,4]) price for XOM for 50 days

    # Calculate avg daily returns on benchmark and portfolio
    na_normalized_price_portfolio_perday = na_normalized_price_portfolio.copy()
    tsu.returnize0(na_normalized_price_portfolio_perday)

    na_normalized_price_benchmark_perday = na_normalized_price_benchmark.copy()
    tsu.returnize0(na_normalized_price_benchmark_perday)

    daily_ret_portfolio = np.average(na_normalized_price_portfolio_perday)
    daily_ret_benchmark = np.average(na_normalized_price_benchmark_perday)
    # daily_ret = np.average(na_weighted_rets)

    # get standard dev of weighted returns
    vol_portfolio = np.std(na_normalized_price_portfolio_perday)
    vol_benchmark = np.std(na_normalized_price_benchmark_perday)
    # vol = np.std(na_weighted_rets)

    # Sharpe ratio = (Mean portfolio return - Risk-free rate)/Standard deviation of portfolio return
    # problem states "Always assume you have 252 trading days in an year. And risk free rate = 0"
    sharpe_portfolio = np.sqrt(252) * daily_ret_portfolio / vol_portfolio
    sharpe_benchmark = np.sqrt(252) * daily_ret_benchmark / vol_benchmark

    # cumulative return of total portfolio
    cum_ret_portfolio = portfolio_values[-1] / portfolio_values[0]
    cum_ret_benchmark = na_price_benchmark[-1] / na_price_benchmark[0]

    mult = portfolio_values[0] / na_price_benchmark[0]

    plt.clf()
    plt.plot(ldt_timestamps, portfolio_values)
    plt.plot(ldt_timestamps, na_price_benchmark * mult)
    plt.legend(['Portfolio', 'Benchmark'], loc='best')
    plt.ylabel('Fund Value', size='x-small')
    plt.xlabel('Date', size='x-small')
    locs, labels = plt.xticks(size='x-small')
    plt.yticks(size='x-small')
    plt.setp(labels, rotation=15)
    # for hw3:
    plt.savefig('HW3_Values2.pdf', format='pdf')
    # for hw4:
    # plt.savefig('HW4_CumPortfolioValues.pdf', format='pdf')

    print "Details of the Performance of the portfolio :"
    print "Data Range :", str(dates[0]), " to ", str(dates[-1])
    print "Sharpe Ratio of Fund:", sharpe_portfolio
    print "Sharpe Ratio of $SPX:", sharpe_benchmark
    print "Standard Deviation of Fund: ", vol_portfolio
    print "Standard Deviation of $SPX: ", vol_benchmark
    print "Average Daily Return of Fund:", daily_ret_portfolio
    print "Average Daily Return of $SPX:", daily_ret_benchmark
    print "Total Return of Fund:", cum_ret_portfolio
    print "Total Return of $SPX:", cum_ret_benchmark

    return vol_portfolio, daily_ret_portfolio, sharpe_portfolio, cum_ret_portfolio, vol_benchmark, daily_ret_benchmark, sharpe_benchmark, cum_ret_benchmark


# for hw3:
vol_p, daily_p, sharpe_p, cum_p, vol_b, daily_b, sharpe_b, cum_b = analyze('values2.csv', ['$SPX'])
# for hw4:
# vol_p, daily_p, sharpe_p, cum_p, vol_b, daily_b, sharpe_b, cum_b = analyze('hw4_values.csv', ['$SPX'])

# Example output
# Data Range :  2011-01-05 16:00:00  to  2011-01-20 16:00:00

# Sharpe Ratio of Fund : -0.449182051041
# Sharpe Ratio of $SPX : 0.88647463107

# Total Return of Fund :  0.998035
# Total Return of $SPX : 1.00289841449

# Standard Deviation of Fund :  0.00573613516299
# Standard Deviation of $SPX : 0.00492987789459

# Average Daily Return of Fund :  -0.000162308588036
# Average Daily Return of $SPX : 0.000275297459588

# in this case, if you executed the orders in this strategy,
# you would have lost money during this time period because the Sharpe Ratio is less than 1,
# the Total Return is less than 1, and the Avg. Daily Return is a negative value
# This strategy also performs worse than the benchmark (in this case, $SPX)