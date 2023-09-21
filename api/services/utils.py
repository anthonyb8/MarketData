from typing import TYPE_CHECKING, Optional, Union
from sqlalchemy.orm import Query
import database.models as models
from app.schemas import AssetType
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

def asset_type(asset_type_str: str) -> Optional[AssetType]:
    """
    Convert a string representation of an asset type to the corresponding AssetType enum.

    Parameters:
    - asset_type_str: The string representation of the asset type.

    Returns:
    - An AssetType enum if the conversion is successful.

    Raises:
    - HTTPException if the provided asset type string is invalid.
    """
    try:
        return getattr(AssetType, asset_type_str.upper())
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid asset type.")

def get_asset(db: "Session", ticker: str, asset_type: AssetType) -> models.Asset:
    """
    Retrieve an asset from the database based on its ticker and type.

    Parameters:
    - db: The database session.
    - ticker: The ticker of the asset.
    - asset_type: The type of the asset.

    Returns:
    - An instance of the Asset model or None if not found.
    """
    return db.query(models.Asset).filter_by(ticker=ticker, type=asset_type.type).one_or_none()

def get_details(db: "Session", asset_id: int, asset_type: AssetType) -> Union[models.Equity, models.Cryptocurrency, models.CommodityFuture]:
    """
    Fetch the detailed information of an asset based on its ID and type.

    Parameters:
    - db: The database session.
    - asset_id: The ID of the asset.
    - asset_type: The type of the asset.

    Returns:
    - An instance of the specific asset detail model or None if not found.
    """
    return db.query(asset_type.model).filter_by(asset_id=asset_id).first()

def get_bardata_instance(db: "Session", asset_id: int, date: str, asset_type: AssetType) -> Union[models.EquityBarData, models.CryptocurrencyBarData, models.CommodityFutureBarData]:
    """
    Retrieve the bardata instance for a specific asset based on its ID, date, and type.

    Parameters:
    - db: The database session.
    - asset_id: The ID of the asset.
    - date: The date for which bardata is requested.
    - asset_type: The type of the asset.

    Returns:
    - An instance of the specific bardata model or None if not found.
    """
    return db.query(asset_type.bardata_model).filter_by(asset_id=asset_id, date=date).one_or_none()

def asset_exists(db: "Session", ticker: str, asset_type: AssetType) -> Optional[int]:
    """
    Check if an asset exists in the database based on its ticker and type.

    Parameters:
    - db: The database session.
    - ticker: The ticker of the asset.
    - asset_type: The type of the asset.

    Returns:
    - The asset's ID if it exists or None otherwise.
    """
    asset_instance = get_asset(db=db, ticker=ticker, asset_type=asset_type)
    return asset_instance.asset_id if asset_instance else None

def details_exist(db: "Session", ticker: str, asset_type: AssetType) -> Optional[Union[models.Equity, models.Cryptocurrency, models.CommodityFuture]]:
    """
    Check if detailed information of an asset exists in the database.

    Parameters:
    - db: The database session.
    - ticker: The ticker of the asset.
    - asset_type: The type of the asset.

    Returns:
    - The asset's detail instance if it exists or None otherwise.
    """
    asset_id = asset_exists(db=db, ticker=ticker, asset_type=asset_type)
    details_instance = get_details(db=db, asset_id=asset_id, asset_type=asset_type)
    return details_instance if details_instance else None

def apply_filter_criteria(query: Query, model, filter_criteria: dict) -> Query:
    """
    Modify a query object based on provided filtering criteria.

    Parameters:
    - query: The initial SQL query.
    - model: The database model that the query corresponds to.
    - filter_criteria: A dictionary containing the filtering conditions.

    Returns:
    - The modified query with applied filtering conditions.

    Raises:
    - HTTPException if an invalid attribute is provided in the filter criteria.
    """
    for key, value in filter_criteria.items():
        if hasattr(model, key):
            if "gte" in key:
                attribute = getattr(model, key.split("_")[0])  # Assumes format like "attribute_gte"
                query = query.filter(attribute >= value)
            elif "lte" in key:
                attribute = getattr(model, key.split("_")[0])  # Assumes format like "attribute_lte"
                query = query.filter(attribute <= value)
            else:
                attribute = getattr(model, key)
                query = query.filter(attribute == value)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"'{key}' is not a valid attribute.")
        
    return query

def apply_date_filter(query: Query, model, filter_criteria: dict) -> Query:
    """
    Modify a query object to filter based on date range.

    Parameters:
    - query: The initial SQL query.
    - model: The database model that the query corresponds to.
    - filter_criteria: A dictionary containing the start and end date for filtering.

    Returns:
    - The modified query with applied date range filtering.
    """
    return query.filter((filter_criteria['start_date'] <= model.date) & (filter_criteria['end_date'] >= model.date))

    