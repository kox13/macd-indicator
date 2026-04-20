from utils import *

path = 'data/bitcoin-data.csv'
data = get_data(path)
data = convert_data(data)

plot_prices(data)

ema26 = calc_ema(26, data['Close'])
ema12 = calc_ema(12, data['Close'])
macd = ema12 - ema26
signal = calc_ema(9, macd)

cross_up, cross_down = mark_crosses(macd, signal)

plot_macd_signal(data, macd, signal, cross_up, cross_down)

plot_prices_with_crosses(data, cross_up, cross_down)
plot_between_dates(data, '2024-11-05', '2024-12-22', cross_up, cross_down)
plot_between_dates(data, '2024-11-30', '2025-03-01', cross_up, cross_down)

balance, bitcoins, transactions = simulate_trade(data, cross_up, cross_down)
plot_trade_results(balance, bitcoins, transactions)

