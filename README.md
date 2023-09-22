# MarketDatabaseManager

<p align="left">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg">
</p>

MarketDatabaseManager is your complete solution for interacting with financial assets using a Docker-optimized REST API backed by PostgreSQL.

## 🔥 Features

- **Docker-Optimized REST API**: Efficiently interact with a PostgreSQL database stored in the local PostgreSQL app, all via a REST API encapsulated within a Docker container.
- **Comprehensive Asset Categorization**: Features detailed tables designed specifically for various asset classes, such as equity, cryptocurrency, and commodity futures.
- **Asset-Specific Bar Data Tables**: Each asset class has its own dedicated bar data table, allowing for detailed financial tracking and analysis.
- **User-Friendly**: Intuitive methods are at your disposal to add, modify, or delete financial asset data with ease.
- **Integrated Client Library**: The provided client library facilitates seamless interactions with the API. It acts as a bridge to the local PostgreSQL database, ensuring consistency and efficiency in handling data across all supported asset classes.


## 🚀 Installation

#### 1️⃣ Install PostgreSQL
- [PostgreSQL Official Download](https://www.postgresql.org/download/)

#### 2️⃣ Install Docker
- [Docker Desktop Official Download](https://www.docker.com/products/docker-desktop/)

#### 3️⃣ Create Database
```bash
psql -U postgres;

CREATE DATABASE <database_name>;
```

#### 4️⃣ Clone the repository
```bash
git clone https://github.com/anthonyb8/MarketDatabaseManager.git
```

#### 5️⃣ Set up your environment
Create a `.env` file in the `api` directory and insert your database credentials:
```plaintext
DATABASE_URL = "postgresql://<user>:<password>@host.docker.internal/<database_name>"
```
> ⚠️ Note: If Docker isn't running locally, replace `host.docker.internal` with the appropriate host.

#### 6️⃣ Dockerize
From the root `MarketDatabaseManager` directory, run the following commands to build and start the Docker container:
```bash
docker-compose build

docker-compose up -d
```

#### 7️⃣ Install the client library
While in the root directory of your project (not the `MarketDatabaseManager` directory), execute the following commands to set up the virtual environment and install the client library:
```bash
python3.10 -m venv venv

source venv/bin/activate

pip install MarketDataManager
```

## 📌 Examples

#### Create Database Tables
```python
from MarketDataManager import Client

client = Client()
client.create_tables()
```

#### Create Asset
```python
new_asset = {
    "ticker" : "AAPL", 
    "type" : "equity"
}
client.create_asset(asset = new_asset)
```

#### Add Asset Details
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
client.create_asset_details(ticker="AAPL", asset_type="equity",data=asset_details)
```
#### Add Asset Bardata
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
client.create_bardata(ticker="AAPL", asset_type="equity", data=asset_bardata)
```

## 📜 License

This project is licensed under the Apache License, Version 2.0. [Get a copy of the License here](http://www.apache.org/licenses/LICENSE-2.0).
