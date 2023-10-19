import requests
from urllib.parse import urljoin
import datetime as dt
from typing import List, Optional, Union

class Client:
    """
    A client interface to interact with the Market Data API.
    
    This class provides utility methods that facilitate CRUD (Create, Read, Update, Delete) 
    operations related to assets and their accompanying details.
    
    Attributes:
        BASE_URL (str): Default API base URL.
        base_url (str): Instance-specific base URL.
        session (Session): Persistent session for making HTTP requests.
    """

    BASE_URL = "http://127.0.0.1:8000"  # Default base URL for the API.

    def __init__(self, base_url=None):
        """
        Initializes the client with an optional base URL.
        
        Parameters:
            base_url (str, optional): Specific base URL to override the default. 
                                      If not provided, defaults to BASE_URL.
        """
        self.base_url = base_url or self.BASE_URL
        self.session = requests.Session()  # Persistent session for efficient HTTP requests.

    @staticmethod
    def _error_handling(response):
        """
        Process and handle the response from the API.
        
        Based on HTTP status codes, the method standardizes the response into a success/error format.
        Provides detailed error messages where possible.
        
        Parameters:
            response (Response): HTTP response object from the `requests` library.
        
        Returns:
            dict: Standardized response dictionary.
        """
        # Process responses based on HTTP status codes
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 400:
            return {"success": False, "error": response.json().get("detail", "Unknown error.")}
        elif response.status_code == 404:
            return {"success": False, "error": 'Invalid asset type.'}
        elif response.status_code == 422:
            error_details = response.json().get("detail", [])
            error_messages = [f" '{' -> '.join([part for part in detail.get('loc', []) if part != 'body' and not isinstance(part, int)])}': {detail.get('msg', 'Unknown error')} " for detail in error_details]
            user_friendly_error = " & ".join(error_messages)
            return {'success': False, "error": user_friendly_error}

    def _request(self, method, endpoint, data=None, params=None):
        """
        Internal utility method to construct and make requests to the API.
        
        This method forms the complete URL for requests, sends the request, and then invokes 
        error handling to process the response.
        
        Parameters:
            method (str): The HTTP method (e.g., "get", "post", "put", "delete").
            endpoint (str): The API endpoint to hit, relative to the base URL.
            data (dict, optional): JSON serializable Python object to send in the body of the request.
            params (dict, optional): Dictionary of URL parameters to append to the URL.
        
        Returns:
            dict: Standardized response dictionary.
        """
        url = urljoin(self.base_url, endpoint)
        response = getattr(self.session, method)(url, json=data, params=params)
        return self._error_handling(response)
    
    def test_database_connection(self):
        return self._request("get", "/api/database/connection-check")

    def create_tables(self):
        """
        Initialize and set up the necessary tables in the database.
        
        This method sends a request to the API endpoint responsible for database table creation.
        
        Returns:
            Response object indicating the result of the table creation process.
        """
        return self._request("post", "/api/database/")

    def delete_tables(self):
        """
        Remove all tables from the database, effectively cleaning it.
        
        Warning:
            This is a destructive operation and should be used with caution.
        
        Returns:
            Response object indicating the result of the table deletion process.
        """
        return self._request("delete", "/api/database/")

    def create_asset(self, asset:dict):
        """
        Introduce a new asset record into the system.
        
        Parameters:
            - asset (dict): Dictionary containing details of the asset such as ticker, type, and other related attributes.
        
        Returns:
            Response object containing the result of the asset creation request, which may include the asset ID and other metadata.
        """
        return self._request("post", "/api/asset/", data=asset)

    def get_asset(self, ticker:Optional[str] = None, asset_type:Optional[str] = None):
        """
        Fetch information about an asset or assets. The retrieval can be based on a specific ticker and/or asset type.
        
        Parameters:
            - ticker (Optional[str]): The ticker symbol of the asset to be retrieved. If provided, narrows down the search.
            - asset_type (Optional[str]): The type/category of the asset (e.g., "equity", "cryptocurrency"). 
                                        If provided, filters assets of the specified type.
        
        Returns:
            Response object containing the fetched asset information, which can include a list of assets or details of a specific asset.
        """
        params = {"ticker": ticker, "asset_type": asset_type}
        return self._request("get", "/api/asset/", params=params)

    def delete_asset(self, ticker:str, asset_id:int):
        """
        Remove a specific asset from the system using its ticker and asset_id.
        
        Parameters:
            - ticker (str): The ticker symbol of the asset to be deleted.
            - asset_id (int): The unique identifier of the asset to be deleted.
        
        Returns:
            Response object containing the result of the deletion request.
        """
        params = {"ticker": ticker, "asset_id": asset_id}
        return self._request("delete", "/api/asset/", params=params)

    def create_asset_details(self, ticker:str, asset_type:str, data:dict):
        """
        Add detailed metadata or specifics for a given asset using its ticker and asset type.
        
        Parameters:
            - ticker (str): The ticker symbol of the asset for which the details are to be added.
            - asset_type (str): The type of the asset (e.g., "equity", "cryptocurrency").
            - data (dict): Dictionary containing the detailed fields and their respective values for the asset.
        
        Returns:
            Response object containing the result of the creation request.
        """
        endpoint = f"/api/{asset_type}/{ticker}/"
        return self._request("post", endpoint, data=data)

    def get_asset_details(self, asset_type:str, ticker:Optional[str]=None, filter_criteria: Optional[dict]=None):
        """
        Fetch detailed information about assets. The retrieval can be based on a specific asset type and ticker, 
        or filtered based on provided criteria.
        
        Parameters:
            - asset_type (str): The type of assets for which details are to be retrieved.
            - ticker (Optional[str]): A specific ticker symbol to retrieve details for a single asset. If provided, takes priority.
            - filter_criteria (Optional[dict]): Dictionary of criteria to filter the assets for retrieval. Used when ticker is not provided.
        
        Returns:
            Response object containing the fetched asset details.
        """
        if ticker:
            endpoint = f"/api/{asset_type}/{ticker}"
            return self._request("get", endpoint)
        elif filter_criteria:
            endpoint = f"/api/{asset_type}"
            return self._request("post", endpoint, data=filter_criteria)

    def create_bardata(self, ticker:str, asset_type:str, data:dict):
        """
        Create new bar data entry for a specific asset based on its ticker and asset type.
        
        Parameters:
            - ticker (str): The ticker symbol of the asset.
            - asset_type (str): The type of the asset (e.g., "equity", "cryptocurrency").
            - data (dict): Dictionary containing the bar data fields and their respective values.
        
        Returns:
            Response object containing the result of the creation request.
        """
        endpoint = f"/api/{asset_type}/{ticker}/bardata/"
        return self._request("post", endpoint, data=data)

    def get_bardata(self, tickers:Union[List[str], str], start_date:str, end_date:Optional[str] = None):
        """
        Retrieve historical bar data for a set of tickers within a specified date range.
        
        Parameters:
            - tickers (Union[List[str], str]): A single ticker or a list of tickers for which to fetch the bar data.
            - start_date (str): The start date of the desired data range in 'YYYY-MM-DD' format.
            - end_date (Optional[str]): The end date of the desired data range in 'YYYY-MM-DD' format.
                                    If not provided, the current date is used.
        
        Returns:
            Response object containing the retrieved bar data.
        """
        data = {
            'tickers': tickers,
            'start_date': start_date,
            'end_date': end_date if end_date else dt.datetime.now().strftime('%Y-%m-%d')
        }
        return self._request("post", "/api/bardata/", data=data)

    def edit_asset(self, asset_id:int, edits:dict):
        """
        Edit the basic details of an asset using its asset_id.
        
        Parameters:
            - asset_id (int): The unique identifier for the asset.
            - edits (dict): Dictionary containing the fields and values to be updated.
        
        Returns:
            Response object containing the result of the edit request.
        """
        endpoint = f"/api/asset/{asset_id}"
        return self._request("put", endpoint, data=edits)

    def edit_asset_details(self, asset_id:int, asset_type:str, edits:dict):
        """
        Edit detailed attributes of a specific asset based on its asset_id and asset type.
        
        Parameters:
            - asset_id (int): The unique identifier for the asset.
            - asset_type (str): The type of the asset (e.g., "equity", "cryptocurrency").
            - edits (dict): Dictionary containing the fields and values to be updated.
        
        Returns:
            Response object containing the result of the edit request.
        """
        endpoint = f"/api/{asset_type}/{asset_id}"
        return self._request("put", endpoint, data=edits)

    def edit_bardata(self, asset_id:int, asset_type:str, edits:dict):
        """
        Edit the bar data (historical data points) of a specific asset based on its asset_id and asset type.
        
        Parameters:
            - asset_id (int): The unique identifier for the asset.
            - asset_type (str): The type of the asset (e.g., "equity", "cryptocurrency").
            - edits (dict): Dictionary containing the bar data fields and values to be updated.
        
        Returns:
            Response object containing the result of the edit request.
        """
        endpoint = f"/api/{asset_type}/bardata/{asset_id}"
        return self._request("put", endpoint, data=edits)

