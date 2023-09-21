import datetime as dt
import pydantic as pydantic
from pydantic import validator
import database.models as models
from enum import Enum
from typing import Optional, List, Union

# Asset Schemas
class _BaseAsset(pydantic.BaseModel):
    """
    Base schema for assets with common attributes and validators.
    """
    ticker: str
    type: str

    @validator('ticker', pre=True, always=True)
    def uppercase_ticker(cls, v):
        """
        Ensure the ticker is always in uppercase.
        """
        return v.upper()

    @validator('type', pre=True, always=True)
    def lowercase_type(cls, v):
        """
        Ensure the asset type is always in lowercase.
        """
        return v.lower()

class RetrieveAsset(_BaseAsset):
    """
    Schema for retrieving an asset, includes timestamps.
    """
    asset_id: int
    created_at: dt.datetime
    updated_at: dt.datetime

    class Config:
        from_attributes = True

class CreateAsset(_BaseAsset):
    """
    Schema for creating a new asset.
    """
    pass

# Equity Schemas
class _BaseEquity(pydantic.BaseModel):
    """
    Base schema for equities with common attributes.
    """
    company_name: str
    exchange: str
    currency: str
    industry: str
    description: str
    market_cap: int
    shares_outstanding: int

class CreateEquity(_BaseEquity):
    """
    Schema for creating a new equity.
    """
    pass

class RetrieveEquity(_BaseEquity):
    """
    Schema for retrieving an equity, includes asset and equity IDs and timestamps.
    """
    asset_id: int
    equity_id: int
    created_at: dt.datetime
    updated_at: dt.datetime

# Cryptocurrency Schemas
class _BaseCryptocurrency(pydantic.BaseModel):
    """
    Base schema for cryptocurrencies with common attributes.
    """
    cryptocurrency_name: str
    circulating_supply: int
    market_cap: int
    total_supply: int
    max_supply: int
    description: str

class CreateCryptocurrency(_BaseCryptocurrency):
    """
    Schema for creating a new cryptocurrency.
    """
    pass

class RetrieveCryptocurrency(_BaseCryptocurrency):
    """
    Schema for retrieving a cryptocurrency, includes asset and cryptocurrency IDs and timestamps.
    """
    asset_id: int
    cryptocurrency_id: int
    created_at: dt.datetime
    updated_at: dt.datetime

# Commodity Futures Schemas
class _BaseCommodityFuture(pydantic.BaseModel):
    """
    Base schema for commodity futures with common attributes.
    """
    commodity_name: str
    base_future_code: str
    expiration_date: Union[dt.datetime, dt.date]
    industry: str
    exchange: str
    currency: str
    description: str

class CreateCommodityFuture(_BaseCommodityFuture):
    """
    Schema for creating a new commodity future.
    """
    pass

class RetrieveCommodityFuture(_BaseCommodityFuture):
    """
    Schema for retrieving a commodity future, includes asset and commodity future IDs and timestamps.
    """
    asset_id: int
    commodity_future_id: int
    created_at: dt.datetime
    updated_at: dt.datetime

# Bardata Schemas
class _BaseBardata(pydantic.BaseModel):
    """
    Base schema for bar data with common attributes.
    """
    date: Union[dt.datetime, dt.date]
    open: Optional[float] = 0.0
    close: Optional[float] = 0.0
    high: Optional[float] = 0.0
    low: Optional[float] = 0.0
    volume: Optional[int] = 0.0
    adjusted_close: Optional[float] = None

class CreateBardata(_BaseBardata):
    """
    Schema for creating new bar data. Excludes the 'adjusted_close' field if its value is None.
    """
    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        if data.get("adjusted_close") is None:
            data.pop("adjusted_close")
        return data

class RetrieveBardata(_BaseBardata):
    """
    Schema for retrieving bar data. Includes the asset ID and excludes the 'adjusted_close' field if its value is None.
    """
    asset_id: int

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        if data.get("adjusted_close") is None:
            data.pop("adjusted_close")
        return data

class BardataFilter(pydantic.BaseModel):
    """
    Schema for filtering bar data based on tickers and date range.
    """
    tickers: List[str]
    start_date: Union[dt.datetime, dt.date]
    end_date: Optional[Union[dt.datetime, dt.date]] = None

    @validator("end_date", pre=True, always=True)
    def set_end_date_default(cls, value):
        """
        Set the end date to the current datetime if it's not provided.
        """
        return value or dt.datetime.now()

# Enum for models and schemas
class AssetType(Enum):
    """
    Enum class for different asset types and their associated database models.
    """
    EQUITY = ("equity", models.Equity, models.EquityBarData, _BaseEquity)
    CRYPTOCURRENCY = ("cryptocurrency", models.Cryptocurrency, models.CryptocurrencyBarData, _BaseCryptocurrency)
    COMMODITYFUTURE = ("commodityfuture", models.CommodityFuture, models.CommodityFutureBarData, _BaseCommodityFuture)

    def __init__(self, type, model, bardata_model, base_schema):
        self._type = type
        self._model = model
        self._bardata_model = bardata_model
        self._base_schema = base_schema

    @property
    def type(self):
        """
        Return the asset type.
        """
        return self._type

    @property
    def model(self):
        """
        Return the database model associated with the asset type.
        """
        return self._model

    @property
    def bardata_model(self):
        """
        Return the bar data model associated with the asset type.
        """
        return self._bardata_model

    @property
    def base_schema(self):
        """
        Return the base schema associated with the asset type.
        """
        return self._base_schema
