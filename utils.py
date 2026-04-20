import pandas as pd
import matplotlib.pyplot as plt

def get_data(path):
    data = pd.read_csv(path)
    return data;

def convert_data(data):
    data['Date'] = pd.to_datetime(data['Date'], format='%d.%m.%Y')
    data['Close'] = data['Close'].str.replace('.', '').str.replace(',', '.').astype(float)
    data['Open'] = data['Open'].str.replace('.', '').str.replace(',', '.').astype(float)
    data['High'] = data['High'].str.replace('.', '').str.replace(',', '.').astype(float)
    data['Low'] = data['Low'].str.replace('.', '').str.replace(',', '.').astype(float)
    data['Change'] = data['Change'].str.replace('%', '').str.replace(',', '.').astype(float) / 100
    
    def convert_volume(vol):
        vol = str(vol).replace('.', '').replace(',', '.')
        if vol[-1].isalpha():
            multiplier = {'K': 1e3, 'M': 1e6, 'B': 1e9}.get(vol[-1].upper(), 1)
            return float(vol[:-1]) * multiplier
        return float(vol)
    
    data['Volume'] = data['Volume'].apply(convert_volume)
    data = data.iloc[::-1].reset_index(drop=True);
    
    return data

def calc_ema(span, data):
    alpha = 2 / (span + 1)
    ema = pd.Series(index=data.index, dtype=float)

    ema.iloc[0] = data.iloc[0]

    for i in range(1, len(data)):
        ema.iloc[i] = alpha * data.iloc[i] + (1 - alpha) * ema.iloc[i - 1]

    return ema

def mark_crosses(macd, signal):
    cross_up = pd.Series([False] * len(macd))
    cross_down = pd.Series([False] * len(macd))

    for i in range(1, len(macd)):
        if signal[i-1] > macd[i-1] and signal[i] < macd[i]:
            cross_up[i] = True
        elif signal[i-1] < macd[i-1] and signal[i] > macd[i]:
            cross_down[i] = True
        elif signal[i-1] == macd[i-1] and i > 1:
            if signal[i-2] > macd[i-2] and signal[i] < macd[i]:
                cross_up[i-1] = True
            elif signal[i-2] < macd[i-2] and signal[i] > macd[i]:
                cross_down[i-1] = True

    return cross_up, cross_down

def plot_between_dates(data, start_date, end_date, cross_up, cross_down):
    mask = (data['Date'] >= start_date) & (data['Date'] <= end_date)
    filtered_data = data.loc[mask]
    filtered_cross_up = cross_up.loc[mask]
    filtered_cross_down = cross_down.loc[mask]

    plt.figure(figsize=(10, 5))
    plt.plot(filtered_data['Date'], filtered_data['Close'], label='Ostatnia cena', color='blue')
    plt.scatter(filtered_data['Date'][filtered_cross_up], filtered_data['Close'][filtered_cross_up], color='green', marker='^', label='Kupno (MACD ↑ Signal)', zorder=2)
    plt.scatter(filtered_data['Date'][filtered_cross_down], filtered_data['Close'][filtered_cross_down], color='red', marker='v', label='Sprzedaż (MACD ↓ Signal)', zorder=2)
    plt.xlabel('Data')
    plt.ylabel('Cena')
    plt.title(f'Bitcoin - Ceny zamknięcia z oznaczonymi punktami przecięcia MACD i Signal ({start_date} do {end_date})')
    plt.legend()
    plt.show()

def plot_macd_signal(data, macd, signal, cross_up, cross_down):
    plt.figure(figsize=(10, 5))
    plt.plot(data['Date'], macd, label='MACD', color='blue')
    plt.plot(data['Date'], signal, label='Signal', color='orange')

    plt.scatter(data['Date'][cross_up], macd[cross_up], color='green', marker='^', label='Kupno (MACD ↑ Signal)', zorder=2)
    plt.scatter(data['Date'][cross_down], macd[cross_down], color='red', marker='v', label='Sprzedaż (MACD ↓ Signal)', zorder=2)

    plt.xlabel('Data')
    plt.ylabel('Wartość')
    plt.title('Bitcoin - MACD i Signal z oznaczonymi punktami przecięcia')
    plt.legend()
    plt.show()

def plot_prices(data):
    plt.figure(figsize=(10, 5))
    plt.plot(data['Date'], data['Close'], label='Ostatnia cena', color='blue')
    plt.xlabel('Data')
    plt.ylabel('Cena')
    plt.title('Bitcoin - Ceny zamknięcia z danego dnia od 01.03.2022 do 01.03.2025')
    plt.legend()
    plt.show()

def plot_prices_with_crosses(data, cross_up, cross_down):
    plt.figure(figsize=(10, 5))
    plt.plot(data['Date'], data['Close'], label='Ostatnia cena', color='blue')
    plt.scatter(data['Date'][cross_up], data['Close'][cross_up], color='green', marker='^', label='Kupno (MACD ↑ Signal)', zorder=2)
    plt.scatter(data['Date'][cross_down], data['Close'][cross_down], color='red', marker='v', label='Sprzedaż (MACD ↓ Signal)', zorder=2)
    plt.xlabel('Data')
    plt.ylabel('Cena')
    plt.title('Bitcoin - Ceny zamknięcia z oznaczonymi punktami przecięcia MACD i Signal')
    plt.legend()
    plt.show()

def simulate_trade(data, cross_up, cross_down):
    bitcoins = 1000
    balance = 0
    transaction_fee = 0.001
    purchases = 0
    sales = 0

    buy_price = 0

    gain = 0
    loss = 0

    balances = []
    bitcoins_a = []
    transactions = []

    for i in range(0, len(data) - 26):
        price = data['Close'][i]
        if cross_down[i]:
            if bitcoins > 0:
                balance += bitcoins * price * (1 - transaction_fee)
                bitcoins = 0
                sales += 1

                if buy_price > price:
                    loss += 1
                elif buy_price < price:
                    gain += 1

                balances.append(balance)
                bitcoins_a.append(bitcoins)
                transactions.append(purchases + sales)

        elif cross_up[i]:
            if balance > 0 and price <= balance:
                bitcoins = balance / price * (1 - transaction_fee)
                balance = 0
                purchases += 1
                buy_price = price

                balances.append(balance)
                bitcoins_a.append(bitcoins)
                transactions.append(purchases + sales)

    final_value = balance + bitcoins * data['Close'][len(data)-1]
    print("\nFull trade simulation:")
    print(f"Starting value: {1000 * data['Close'][0]}")
    print(f"Final value: {final_value}")
    print(f"Number of trades: {purchases + sales}")
    print(f"Number of purchases: {purchases}")
    print(f"Number of sales: {sales}")
    print(f"Gains: {gain}")
    print(f"Losses: {loss}\n")

    return balances, bitcoins_a, transactions

def plot_trade_results(balances, bitcoins_a, transactions):
    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(transactions, balances, marker='o', linestyle='-')
    plt.title('Balance over Transactions')
    plt.xlabel('Transaction Number')
    plt.ylabel('Balance')
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(transactions, bitcoins_a, marker='o', linestyle='-')
    plt.title('Bitcoins over Transactions')
    plt.xlabel('Transaction Number')
    plt.ylabel('Bitcoins')
    plt.grid(True)

    plt.tight_layout()
    plt.show()