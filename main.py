
import requests
import pandas as pd
import time
import matplotlib.pyplot as plt
import json
def fetch_nifty50_data():
    """
    Retrieve Nifty 50 stock data from the NSE API.
    """
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050",
    }
    
    session = requests.Session()
    session.headers.update(headers)
    session.get("https://www.nseindia.com", headers=headers)
    time.sleep(2)
    
    response = session.get(url)
    return response.json() if response.status_code == 200 else None

def get_movers(data, count=5):
    """
    Extracts top gainers and losers based on percentage change.
    """
    df = pd.DataFrame(data['data']).sort_values(by='pChange', ascending=False)
    return df.head(count), df.tail(count)[::-1]

def find_discounted_stocks(data, drop_threshold=30):
    """
    Finds stocks trading significantly below their 52-week high.
    """
    df = pd.DataFrame(data['data'])
    df['drop_from_high'] = ((df['yearHigh'] - df['lastPrice']) / df['yearHigh']) * 100
    return df[df['drop_from_high'] >= drop_threshold].nlargest(5, 'drop_from_high')

def find_rebounding_stocks(data, rise_threshold=20):
    """
    Finds stocks that have rebounded significantly from their 52-week low.
    """
    df = pd.DataFrame(data['data'])
    df['rise_from_low'] = ((df['lastPrice'] - df['yearLow']) / df['yearLow']) * 100
    return df[df['rise_from_low'] >= rise_threshold].nlargest(5, 'rise_from_low')

def top_30_day_performers(data):
    """
    Identifies stocks with the highest returns over the past 30 days.
    """
    df = pd.DataFrame(data['data'])
    return df.nlargest(5, 'perChange30d') if 'perChange30d' in df.columns else df.nlargest(5, 'pChange')

def visualize_gainers_losers(gainers, losers):
    """
    Plots a bar chart for top gainers and losers.
    """
    plt.figure(figsize=(10, 6))
    
    plt.subplot(2, 1, 1)
    plt.bar(gainers['symbol'], gainers['pChange'], color='green')
    plt.title('Top Gainers')
    plt.ylabel('Change (%)')
    plt.xticks(rotation=45)
    
    plt.subplot(2, 1, 2)
    plt.bar(losers['symbol'], losers['pChange'], color='red')
    plt.title('Top Losers')
    plt.ylabel('Change (%)')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('stock_movers.png')
    plt.close()

def main():
    print("Fetching market data...")
    stock_data = fetch_nifty50_data()
    
    if stock_data:
        gainers, losers = get_movers(stock_data)
        discounted = find_discounted_stocks(stock_data)
        rebounding = find_rebounding_stocks(stock_data)
        top_performers = top_30_day_performers(stock_data)
        
        print("\nTop 5 Gainers:")
        print(gainers[['symbol', 'lastPrice', 'pChange']])
        
        print("\nTop 5 Losers:")
        print(losers[['symbol', 'lastPrice', 'pChange']])
        
        print("\nStocks Below 52-Week High:")
        print(discounted[['symbol', 'lastPrice', 'yearHigh', 'drop_from_high']])
        
        print("\nStocks Rebounding from 52-Week Low:")
        print(rebounding[['symbol', 'lastPrice', 'yearLow', 'rise_from_low']])
        
        print("\nBest Performers (30 Days):")
        print(top_performers[['symbol', 'lastPrice', 'perChange30d' if 'perChange30d' in top_performers else 'pChange']])
        
        print("\nGenerating visual representation...")
        visualize_gainers_losers(gainers, losers)
        
        with open('market_data.json', 'w') as f:
            json.dump(stock_data, f, indent=2)
        print("Data saved successfully.")
    else:
        print("Failed to retrieve data. Try again later.")

if __name__ == "__main__":
    main()
