# MarketData

![python](https://img.shields.io/badge/python-3.8+-blue.svg)

Key features include:
- Docker-Optimized REST API: Efficiently interact with a PostgreSQL database stored in the local PostgreSQL app, all via a REST API encapsulated within a Docker container.
- Comprehensive Asset Categorization: Features detailed tables designed specifically for various asset classes, such as equity, cryptocurrency, and commodity futures.
- Asset-Specific Bar Data Tables: Each asset class has its dedicated bar data table, allowing for detailed financial tracking and analyses.
- User-Friendly Data Management: Intuitive methods are at your disposal to add, modify, or delete financial asset data with ease.
- Integrated Client Library: The provided client library facilitates seamless interactions with the API. It acts as a bridge to the local PostgreSQL database, ensuring consistency and efficiency in handling data across all supported asset classes.

## Installation

### 1. Install PostgreSQL

https://www.postgresql.org/download/

### 2. Install Docker

https://www.docker.com/products/docker-desktop/

### 3. Create database and user(optional)

```
psql - U postgres;
```
```
CREATE DATABASE <database_name>;
```

### 4. Clone repository to local directory

```
git clone https://github.com/anthonyb8/MarketData.git
```

### 5. Create .env file in api directory
Add the below variable to a .env file in the api directory and update database credentials. 
- Note: If Docker is not running locally, host.docker.internal will have to be updated to the correct host.
```
DATABASE_URL = "postgresql://<user>:<password>@host.docker.internal/<database_name>"
```

### 6. Create the Docker image and container
Below commands must be made from the root MarketData directory.
```
docker-compose build
```
```
docker-compose up -d
```

### 7. Install client library
```
pip install MarketDataClient
```

## Examples

### 1. Create Asset
```python
client = MarketDataClient()

new_asset = {
    "ticker" : "AAPL", 
    "type" : "equity"
}

response = client.create_asset(asset = new_asset)

```

### 2. Add Asset Details
```python
asset_details = {
    'company_name' : 'Apple Inc.',
    'exchange' : 'NASDAQ',
    'currency' :  'USD',
    'industry' : 'Technology',
    'description' : 'Equity for Apple Inc. a technologies producer.',
    'market_cap' : 100000,
    'shares_outstanding' : 100000
}

response = client.create_asset_details(ticker="AAPL", asset_type="equity",data=asset_details)

```
### 3. Add Asset Bardata
```python
asset_bardata =  [
    {
        'date' : '2023-01-01',
        'open': 100.0,
        'close': 101.0,
        'high': 102.0,
        'low': 103,
        'volume': 109,
        'adjusted_close' : 1100.0
    }, 
    {
        'date' : '2023-01-02',
        'open': 100.0,
        'close': 101.0,
        'high': 102.0,
        'low': 103,
        'volume': 109,
        'adjusted_close' : 1100.0
    }
]

response = client.create_bardata(ticker="AAPL", asset_type="equity", data=asset_bardata)

```

## License

This project is licensed under the Apache License, Version 2.0. You may obtain a copy of the License at:

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)
