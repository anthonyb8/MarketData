import psycopg2
import unittest
import logging, sys
from MarketDataClient.client import Client
from typing import Optional, List, Dict

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

#Base class for set up and teardown
class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        try:
            cls.client.delete_tables()
            cls.client.create_tables()
        except Exception as e:
            print(f"Error encountered: {e}")

    def setUp(self) -> None:
        self.asset = {
            'ticker': Optional[str],
            'type': Optional[str]
            }
        
        self.equity_data = {
            'company_name' : 'Apple',
            'exchange' : 'NASDAQ',
            'currency' :  'USD',
            'industry' : 'Technology',
            'description' : 'This is a technology manufacturer',
            'market_cap' : 101010,
            'shares_outstanding' : 101010
            }

        self.cryptocurrency_data = {
            'cryptocurrency_name' : 'Bitcoin', 
            'circulating_supply' : 1091092,
            'market_cap' : 3476356,
            'total_supply' : 55355,
            'max_supply' : 44434343,
            'description' : 'Decentralized currency.'
        }

        self.commodity_data = {
            'commodity_name': 'Crude Oil',
            'base_future_code' : 'CL',
            'expiration_date' : '2023-09-20',
            'industry' : 'Energy',
            'exchange' : 'CME',
            'currency' : 'USD',
            'description' : 'October future contract on Crude Oil.' 
        }

        self.equity_bardata =  {
            'date' : '2023-01-01',
            'open': 100.0,
            'close': 101.0,
            'high': 102.0,
            'low': 103,
            'volume': 109,
            'adjusted_close' : 1100.0
        }
        
        self.cryptocurrency_bardata =   {
            'date' : '2023-09-10',
            'open': 100.0,
            'close': 101.0,
            'high': 102.0,
            'low': 103,
            'volume': 109
        }
        
        self.commodity_bardata =   {
            'date' : '2023-09-10',
            'open': 100.0,
            'close': 101.0,
            'high': 102.0,
            'low': 103,
            'volume': 109
        }

class TestCreateAsset(BaseTest):
        
    def test_create_asset_valid(self):
        self.asset['ticker'] = 'AAPL'
        self.asset['type'] = 'equity'

        response = self.client.create_asset(self.asset)
        self.assertTrue(response['success'])

    def test_create_asset_missing_type(self):
        self.asset['ticker'] = 'CLV3'
        self.asset['type'] = ''

        response = self.client.create_asset(self.asset)
        self.assertEqual(response['error'],'Asset type is missing.')

    def test_create_asset_missing_ticker(self):
        self.asset['ticker'] = ''
        self.asset['type'] = 'commodityfuture'

        response = self.client.create_asset(self.asset)
        self.assertEqual(response['error'],'Ticker is missing.')
    
    def test_create_asset_invlaid_type(self):
        self.asset['ticker'] = 'TSLA'
        self.asset['type'] = 'Invalid'
        reponse = self.client.create_asset(self.asset)
        self.assertEqual(reponse['error'], "Invalid asset type.")

    def test_create_duplicate_asset(self):
        self.asset['ticker'] = 'TSLA'
        self.asset['type'] = 'equity'

        self.client.create_asset(self.asset)
        response = self.client.create_asset(self.asset)
        self.assertTrue(response['error'], "Asset already present in 'asset' table.")

class TestCreateAssetDetails(BaseTest):
    def test_create_asset_details_valid(self):
        ticker = 'AAPL'
        type = 'equity'
        self.asset['ticker'] = ticker
        self.asset['type'] = type

        self.client.create_asset(asset= self.asset)
        response = self.client.create_asset_details(ticker=ticker, asset_type=type,data=self.equity_data)
        self.assertTrue(response['success'])

    def test_create_asset_details_nonexistent_asset(self):
        ticker = 'ETH-USD'
        response = self.client.create_asset_details(ticker = ticker, asset_type='cryptocurrency', data= self.cryptocurrency_data)
        self.assertEqual(response['error'],f'Asset {ticker} non-existant in database.')

    def test_asset_details_exists(self):
        ticker = 'BTC-USD'
        type = 'cryptocurrency'
        self.asset['ticker'] = ticker
        self.asset['type'] = type
        self.client.create_asset(asset=self.asset)
        self.client.create_asset_details(ticker=ticker, asset_type=type,data=self.cryptocurrency_data)
        response = self.client.create_asset_details(ticker=ticker, asset_type=type,data=self.cryptocurrency_data)

        self.assertEqual(response['error'],f"Asset already present in {self.asset['type']} table.")

    def test_asset_details_missing_data(self):  
    
        ticker =  'CLV3'
        type= 'commodityfuture'
        self.asset['ticker'] = ticker
        self.asset['type'] = type

        self.client.create_asset(asset=self.asset)

        self.commodity_data["commodityname"] = self.commodity_data["commodity_name"]
        del self.commodity_data["commodity_name"]
        response = self.client.create_asset_details(ticker=ticker, asset_type=type,data=self.commodity_data)
        self.assertEqual(response['error'], " 'commodity_name': Field required ")  

class TestCreateBardata(BaseTest):

    def test_create_bardata_valid(self):
        ticker = 'AAPL'
        type = 'equity'

        self.asset['ticker'] = ticker
        self.asset['type'] = type
    
        self.client.create_asset(asset=self.asset)
        self.client.create_asset_details(ticker=ticker, asset_type=type, data=self.equity_data)

        response = self.client.create_bardata(ticker=ticker, asset_type=type, data=[self.equity_bardata])
        self.assertTrue(response['success'])

    def test_create_bardata_duplicate_date(self):
        ticker = 'CLV3'
        type = 'commodityfuture'

        self.asset['ticker'] = ticker
        self.asset['type'] = type

        self.client.create_asset(asset=self.asset)
        self.client.create_asset_details(ticker=ticker, asset_type=type, data=self.commodity_data)

        self.client.create_bardata(ticker=ticker, asset_type=type, data=[self.commodity_bardata])
        response = self.client.create_bardata(ticker=ticker, asset_type=type, data=[self.commodity_bardata])
        self.assertEqual(response['error'], 'Duplicate date trying to be entered into database.')

    def test_create_bardata_asset_not_in_assetclass_table(self):
        ticker = 'BTC-USD'
        type = 'cryptocurrency'

        self.asset['ticker'] = ticker
        self.asset['type'] = type

        self.client.create_asset(self.asset)

        response = self.client.create_bardata(ticker=ticker, asset_type=type,data=[self.cryptocurrency_bardata])
        self.assertEqual(response['error'],'Asset non-existant in cryptocurrency table.')

    def test_create_bardata_missing_data(self):
        ticker = 'BTC-USD'
        type = 'cryptocurrency'
        missing_category = 'date'

        del self.cryptocurrency_bardata[missing_category]

        response = self.client.create_bardata(ticker=ticker, asset_type=type, data=[self.cryptocurrency_bardata])
        self.assertEqual(response['error'], " 'date': Field required ")

class TestGetAsset(BaseTest):
    
    def test_get_asset_by_ticker(self):
        tickers = ['AAPL', 'TSLA']
        type = 'equity'

        self.asset['ticker'] = tickers[0]
        self.asset['type'] = type
        self.client.create_asset(self.asset)

        self.asset['ticker'] = tickers[1]
        self.client.create_asset(self.asset)

        response = self.client.get_asset(ticker ='TSLA')
        self.assertEqual('TSLA',response['data'][0]['ticker'])

    def test_get_asset_by_type(self):
        tickers = ['CLV3', 'CLZ3']
        type = 'commodityfuture'

        self.asset['ticker'] = tickers[0]
        self.asset['type'] = type
        self.client.create_asset(self.asset)

        self.asset['ticker'] = tickers[1]
        self.client.create_asset(self.asset)

        response = self.client.get_asset(asset_type='commodityfuture')
        queried_tickers = []
        for asset in response['data']: 
            queried_tickers.append(asset['ticker'])

        self.assertEqual(tickers, queried_tickers)

    def test_get_asset_ticker_non_existant(self):
        ticker = 'BTC-USD'
        response = self.client.get_asset(ticker=ticker)
        self.assertEqual(response['error'], f"Asset {ticker} not present in 'asset' table.")

    def test_get_asset_invalid_type(self):
        response = self.client.get_asset(asset_type ='invalid')
        self.assertEqual(response['error'], 'Invalid asset type.')
    
    def test_get_asset_no_assets_of_type(self):
        response = self.client.get_asset(asset_type = 'cryptocurrency')
        self.assertEqual(response['error'], 'No assets for given type.')

class TestGetAssetBarData(BaseTest):
    def _create_all_barata(self, ticker, type, details_obj, bardata_obj):

        self.asset['ticker'] = ticker
        self.asset['type'] = type

        self.client.create_asset(asset=self.asset)
        self.client.create_asset_details(ticker=ticker, asset_type=type, data=details_obj)

        bulk_bardata = []
        for i in range(1, 13):
            bardata_obj['date'] = f"2023-{i:02}-01"
            bulk_bardata.append(bardata_obj.copy())

        self.client.create_bardata(ticker=ticker, asset_type=type,data=bulk_bardata)

    def test_get_bardata_single_ticker(self):
        ticker = 'AAPL'
        self._create_all_barata(ticker, 'equity', self.equity_data, self.equity_bardata)

        response = self.client.get_bardata(['AAPL'], start_date="2023-03-01")
        self.assertTrue(response['success'])

    def test_get_bardata_mutiple_tickers(self):
        tickers = ['CLV3', 'CRZ3']
        for ticker in tickers:
            self._create_all_barata(ticker, 'commodityfuture', self.commodity_data, self.commodity_bardata)

        response = self.client.get_bardata(tickers,  start_date= "2023-03-01", end_date= "2023-09-01")
        queried_tickers = []
        for ticker in response['data']:
            queried_tickers.append(ticker)

        self.assertEqual(tickers, queried_tickers)

    def test_get_bardata_invalid_tickers(self):
        tickers = 'BTC-USD'
        self._create_all_barata(tickers, 'cryptocurrency', self.cryptocurrency_data, self.cryptocurrency_bardata)

        response = self.client.get_bardata('BTC-USD', start_date='2023-01-01')
        self.assertEqual(response['error'], " 'tickers': Input should be a valid list ")

    def test_get_bardata_tickers_not_in_database(self):
        tickers = ['SOL-USD']
        response = self.client.get_bardata(tickers, start_date='2023-01-01')
        self.assertEqual(response['error'],"Asset SOL-USD not present in 'asset' table.")

    def test_get_bardata_for_ticker_with_no_bardata(self):
        tickers = ['F', 'TEST']
        for ticker in tickers: 
            self.asset['ticker'] = ticker
            self.asset['type'] = 'equity'
            self.client.create_asset(self.asset)
            self.client.create_asset_details(self.asset['type'], self.equity_data, ticker)
        
        bar_data = [
            self.equity_bardata
        ]
        self.client.create_bardata('equity', bar_data, 'TEST')

        response = self.client.get_bardata(tickers, start_date ='2022-01-01')

        self.assertTrue(response['success'])
        self.assertEqual(response['data']['F'], [])

class TestDeleteAsset(BaseTest):
    def test_delete_asset(self):
        self.asset['ticker'] = 'DELL'
        self.asset['type'] = 'commodityfuture'

        self.client.create_asset(self.asset)

        self.client.create_asset_details(self.asset['type'], self.commodity_data, self.asset['ticker'])
        self.client.create_bardata(self.asset['type'], [self.commodity_bardata], self.asset['ticker'])
        query_asset = self.client.get_asset(self.asset['ticker'])

        response = self.client.delete_asset(asset_id=query_asset['data'][0]['asset_id'], ticker = query_asset['data'][0]['ticker'])
        self.assertTrue(response['success'])

        # Check infor deleted from all tables
        response = self.client.get_bardata([self.asset['ticker']], start_date='2023-01-01')
        self.assertEqual(response['error'], "Asset DELL not present in 'asset' table.")

class TestEditAsset(BaseTest):
    def test_edit_asset_valid(self):
        self.asset['ticker'] = 'EDT'
        self.asset['type'] = 'equity'
        self.client.create_asset(self.asset)
        old_asset = self.client.get_asset(self.asset['ticker'])
        edits = {
            "ticker": "EDTNEW"
        }

        response = self.client.edit_asset(asset_id=old_asset['data'][0]['asset_id'], edits=edits)
        self.assertEqual(edits['ticker'],  response['data']['ticker'])

    def test_edit_asset_invalid_asset_id(self):
        edits = {
            "ticker": "EDTNEW"
        }
        response = self.client.edit_asset(asset_id=9999, edits=edits)
        self.assertEqual(response['error'], 'Asset with asset_id 9999 not found.')

    def test_edit_asset_type(self):
        self.asset['ticker'] = 'TIT'
        self.asset['type'] = 'equity'
        self.client.create_asset(self.asset)
        db_asset = self.client.get_asset(self.asset['ticker'])
        edits = {
            "type": "invalid"
        }
        response = self.client.edit_asset(asset_id=db_asset['data'][0]['asset_id'], edits=edits)
        self.assertEqual(response['error'], "Asset 'type' cannot be changed, drop asset and re-add under correct asset class.")

    def test_edit_asset_asset_id(self):
        self.asset['ticker'] = 'NUT'
        self.asset['type'] = 'equity'
        self.client.create_asset(self.asset)
        db_asset = self.client.get_asset(self.asset['ticker'])
        edits = {
            "asset_id": 0
        }
        response = self.client.edit_asset(asset_id=db_asset['data'][0]['asset_id'], edits=edits)
        self.assertEqual(response['error'],"Attribute 'asset_id' cannot be changed.")

class TestEditAssetDetails(BaseTest):
    def test_edit_asset_details_valid(self):
        self.asset['ticker'] = 'DETS'
        self.asset['type'] = 'commodityfuture'
        self.client.create_asset(self.asset)
        self.client.create_asset_details(ticker=self.asset['ticker'], asset_type=self.asset['type'], data=self.commodity_data)

        asset = self.client.get_asset(self.asset['ticker'])
        edits = {
            "commodity_name": "newName", 
            "base_future_code": "TL"
        }

        response = self.client.edit_asset_details(asset_id=asset['data'][0]['asset_id'], asset_type='commodityfuture', edits=edits)
        self.assertEqual(edits['commodity_name'], response['data']['commodity_name'])
        self.assertEqual(edits['base_future_code'], response['data']['base_future_code'])

    def test_edit_asset_details_invalid_asset_id(self):
        edits = {
            "description": "EDTNEW"
        }
        response = self.client.edit_asset_details(asset_id=9999,asset_type='equity' ,edits=edits)
        self.assertEqual(response['error'], 'Asset with asset_id 9999 not found.')

    def test_edit_asset_details_no_edits(self):
        edits = {}
        response = self.client.edit_asset_details(asset_id=1,asset_type='cryptocurrency', edits = edits)
        self.assertEqual(response['error'], 'No edits provided.')

    def test_edit_asset_details_details_non_existant(self):
        self.asset['ticker'] = 'CTZ3'
        self.asset['type'] = 'commodityfuture'
        self.client.create_asset(self.asset)

        asset = self.client.get_asset(ticker=self.asset['ticker'])

        edits = {
            "commodity_name": "newName", 
            "base_future_code": "TL"
        }

        response = self.client.edit_asset_details(asset_id=asset['data'][0]['asset_id'], asset_type='commodityfuture',edits=edits)
        self.assertEqual(response['error'], f"Asset with asset_id {asset['data'][0]['asset_id']} not found in '{self.asset['type']}' table.")

    def test_edit_asset_details_invalid_edit(self):
        self.asset['ticker'] = 'LUT3'
        self.asset['type'] = 'commodityfuture'
        self.client.create_asset(self.asset)
        self.client.create_asset_details(ticker=self.asset['ticker'], asset_type=self.asset['type'], data=self.commodity_data)

        asset = self.client.get_asset(self.asset['ticker'])
        edits = {
            "commodityame": "newName", 
        }

        response = self.client.edit_asset_details(asset_id=asset['data'][0]['asset_id'], asset_type='commodityfuture',edits=edits )
        self.assertEqual(response['error'],  "'commodityame' is not a valid attribute.")

class TestEditBardata(BaseTest):
    def test_edit_bardata_valid(self):
        self.asset['ticker'] = 'XRP-USD'
        self.asset['type'] = 'cryptocurrency'
        self.client.create_asset(self.asset)

        self.cryptocurrency_data['cryptocurrency_name'] = "Ripple"
        self.client.create_asset_details(ticker=self.asset['ticker'], asset_type=self.asset['type'], data=self.cryptocurrency_data)

        self.client.create_bardata(ticker=self.asset['ticker'], asset_type=self.asset['type'], data=[self.cryptocurrency_bardata])

        edits ={
            "date" : "2023-09-10", 
            "high" : 9999
        }

        asset = self.client.get_asset(ticker=self.asset['ticker'])
        response = self.client.edit_bardata(asset_id=asset['data'][0]['asset_id'],asset_type=self.asset['type'], edits=edits)
        self.assertEqual(edits['high'], response['data']['high'])

    def test_edit_bardata_invlaid_asset_id(self):
        edits = {
            "date" : "2023-01-01",
            "description": "test"
        }
        response = self.client.edit_bardata(asset_type="equity", asset_id = 9999, edits = edits)
        self.assertEqual(response['error'],'Asset with asset_id 9999 not found.')

    def test_edit_bardata_no_edits(self):
        edits = {}
        response = self.client.edit_bardata(asset_id=1,asset_type='cryptocurrency', edits = edits)
        self.assertEqual(response['error'], 'No edits provided.')

    def test_edit_bardata_bardata_non_existant(self):
        self.asset['ticker'] = 'CTZ3'
        self.asset['type'] = 'commodityfuture'
        self.client.create_asset(self.asset)

        asset = self.client.get_asset(self.asset['ticker'])
        edits = {
            "date" : '2023-09-10'
        }

        response = self.client.edit_bardata(asset_id=asset['data'][0]['asset_id'], asset_type='commodityfuture',edits=edits)
        self.assertEqual(response['error'],f"Asset with asset_id {asset['data'][0]['asset_id']} not found in '{self.asset['type']}_bardata' table.")

    def test_edit_bardata_invalid_edit(self):
        self.asset['ticker'] = 'DOGE-USD'
        self.asset['type'] = 'cryptocurrency'
        self.client.create_asset(self.asset)

        self.cryptocurrency_data['cryptocurrency_name'] = "DOGECOIN"
        self.client.create_asset_details(asset_type=self.asset['type'], data=self.cryptocurrency_data, ticker=self.asset['ticker'])

        self.client.create_bardata(asset_type=self.asset['type'],data=[self.cryptocurrency_bardata], ticker=self.asset['ticker'])

        edits ={
            "date" :"2023-09-10", 
            "hig" : 999
        }
        asset = self.client.get_asset(self.asset['ticker'])

        response = self.client.edit_bardata(asset_type=self.asset['type'], asset_id=asset['data'][0]['asset_id'], edits=edits)
        self.assertEqual(response['error'], "'hig' is not a valid attribute.")

    def test_edit_bardata_no_date(self):
        self.asset['ticker'] = 'SSH-USD'
        self.asset['type'] = 'cryptocurrency'
        self.client.create_asset(self.asset)

        self.cryptocurrency_data['cryptocurrency_name'] = "Shiba"
        self.client.create_asset_details(ticker=self.asset['ticker'], asset_type=self.asset['type'], data=self.cryptocurrency_data)

        self.client.create_bardata(ticker=self.asset['ticker'], asset_type=self.asset['type'],data=[self.cryptocurrency_bardata])

        edits ={
            "dat" :"2023-09-10", 
        }
        asset = self.client.get_asset(self.asset['ticker'])

        response = self.client.edit_bardata(asset_type=self.asset['type'], asset_id=asset['data'][0]['asset_id'], edits=edits)
        self.assertEqual(response['error'],"'date' attribute should be proivided in YYYY-MM-DD format.")

        edits ={
            "date" :"202-09-10", 
        }
        response = self.client.edit_bardata(asset_type=self.asset['type'], asset_id=asset['data'][0]['asset_id'], edits=edits)
        self.assertEqual(response['error'],"'date' attribute should be proivided in YYYY-MM-DD format.")

class TestGetAssetDetails(BaseTest): 
    def test_get_asset_details_by_ticker(self):
        ticker = 'AAPL'
        type ='equity'

        self.asset['ticker'] = ticker
        self.asset['type'] = type
        self.client.create_asset(self.asset)
        self.client.create_asset_details(ticker=ticker, asset_type =type, data=self.equity_data)

        response = self.client.get_asset_details(type, ticker)
        self.assertEqual(response['data'][0]['company_name'],'Apple')
    
    def test_get_asset_details_by_nonexistant_ticker(self):
        self.asset['ticker'] = 'TLR4'
        self.asset['type'] = 'commodityfuture' 
        response = self.client.get_asset_details(asset_type=self.asset['type'], ticker=self.asset['ticker'])
        self.assertEqual(response['error'],  "Asset not present in 'asset' table.")

    def test_get_asset_details_invalid_type(self):
        self.asset['ticker'] = 'TLR4'
        self.asset['type'] = 'commodityfuture' 
        self.client.create_asset(self.asset)
        response = self.client.get_asset_details(asset_type='invalid', ticker='TLR4')
        self.assertEqual(response['error'],'Invalid asset type.')

    def test_get_asset_details_by_filter(self):
        self.asset['ticker'] =  'CLV3'
        self.asset['type'] = 'commodityfuture'
        self.client.create_asset(self.asset)
        self.client.create_asset_details(ticker=self.asset['ticker'], asset_type=self.asset['type'], data=self.commodity_data)


        self.asset['ticker'] =  'ZZV3'
        self.asset['type'] = 'commodityfuture'
        self.client.create_asset(self.asset)
        self.commodity_data['exchange'] = 'NOTCME'
        self.client.create_asset_details(ticker=self.asset['ticker'], asset_type=self.asset['type'], data=self.commodity_data)


        filter = {
            'exchange': 'CME'
        }
        response = self.client.get_asset_details('commodityfuture', filter_criteria=filter)
        for asset in response['data']:
            self.assertEqual(asset['exchange'],filter['exchange'])

    def test_get_asset_detials_nonexistant_details(self):
        ticker = 'TTV3'
        type ='commodityfuture'

        self.asset['ticker'] = ticker
        self.asset['type'] = type
        self.client.create_asset(self.asset)

        response = self.client.get_asset_details('commodityfuture', ticker =self.asset['ticker'])
        self.assertEqual(response['error'], f"Asset not present in '{type}' table.")

    def test_get_asset_details_no_parameters(self):
        response = self.client.get_asset_details('commodityfuture')
        self.assertEqual(response, None)

    def test_get_asset_details_invalid_filter_category(self):
        self.asset['ticker'] = 'BTC-USD'
        self.asset['type'] = 'cryptocurrency'
        self.client.create_asset(self.asset)
        self.client.create_asset_details(ticker=self.asset['ticker'], asset_type=self.asset['type'], data=self.cryptocurrency_data)

        filter = {
            'invalid': 'Bitcoin'
        }
        response = self.client.get_asset_details(asset_type=self.asset['type'], filter_criteria=filter)
        self.assertEqual(response['error'], f"'invalid' is not a valid attribute.")