from MarketDataManager import Client
from utils import RandomBardata

client = Client()
client.create_tables()

new_asset = {
    "ticker" : "MSFT", 
    "type" : "equity"
}
asset_details = {
    'company_name' : 'Microsoft Inc.',
    'exchange' : 'NASDAQ',
    'currency' :  'USD',
    'industry' : 'Technology',
    'description' : 'Equity for Micorsoft Inc. a technologies producer.',
    'market_cap' : 1898979,
    'shares_outstanding' : 1474846
}

generator = RandomBardata()
generator.create_bars(200)
asset_bardata = generator.bardata

client.create_asset(asset = new_asset)
client.create_asset_details(ticker=new_asset['ticker'], asset_type=new_asset['type'],data=asset_details)
client.create_bardata(ticker=new_asset['ticker'], asset_type=new_asset['type'], data=asset_bardata)
