from typing import TYPE_CHECKING, List, Optional, Dict
import database.models as models
from app.schemas import AssetType
import app.schemas as schemas 
import pydantic
from typing import Union, Tuple
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, NoResultFound
if TYPE_CHECKING:
    from sqlalchemy.orm import Session
import re

import services.utils as utils

# =================== POST Services =================== 
# These services create new entries in the database.
async def create_asset(db: "Session", asset: pydantic.BaseModel) -> schemas.RetrieveAsset:
    """
    Create a new asset in the database.

    Parameters:
    - db: Database session.
    - asset: Asset data (ticker, type).

    Returns:
    - new_asset: The newly created asset.
    - True: Operation success status.
    """

    if not asset.ticker:  
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticker is missing.")
    if not asset.type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset type is missing.")

    asset_type = utils.asset_type(asset.type)

    if utils.asset_exists(db=db, ticker = asset.ticker,asset_type=asset_type):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset already present in 'asset' table.")
    
    new_asset = models.Asset(**asset.dict())

    try:
        db.add(new_asset)
        db.commit()
        db.refresh(new_asset)
    except Exception as e:
        db.rollback()  # Rollback for any unexpected error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    return new_asset, True

async def add_details(db: "Session", ticker:str, asset_type:str,  data: pydantic.BaseModel) -> Tuple[Union[pydantic.BaseModel, str], bool]:
    """
    Add details to an existing asset in the database.

    Parameters:
    - db: Database session.
    - ticker: Ticker of the asset.
    - asset_type: Type of the asset (e.g. Equity, Bond).
    - data: Additional details of the asset.

    Returns:
    - db_obj: The asset with added details.
    - True: Operation success status.
    """
    
    asset_type = utils.asset_type(asset_type)

    if utils.details_exist(db=db, ticker=ticker, asset_type=asset_type):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset already present in {asset_type.type} table.")

    asset = utils.get_asset(db=db, ticker=ticker, asset_type=asset_type)

    if not asset:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset {ticker} non-existant in database.")

    
    db_obj = asset_type.model(**data.dict())
    db_obj.asset_id = asset.asset_id
    
    try:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    except Exception as e:
        db.rollback()  # Rollback for any unexpected error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    return db_obj, True

async def add_bardata(db:"Session", ticker:str, asset_type: str,  data: List[pydantic.BaseModel]):
    """
    Add bar data (timeseries data) to an asset in the database.

    Parameters:
    - db: Database session.
    - ticker: Ticker of the asset.
    - asset_type: Type of the asset (e.g. Equity, Bond).
    - data: List of bar data entries.

    Returns:
    - db_objs: List of assets with added bar data.
    - True: Operation success status.
    """
    
    asset_type = utils.asset_type(asset_type)

    asset_details = utils.details_exist(db, ticker, asset_type)

    if not asset_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset non-existant in {asset_type.type} table.")

    db_objs = []
    for entry in data:
        db_obj = asset_type.bardata_model(**entry.dict())
        db_obj.asset_id = asset_details.asset_id
        db_objs.append(db_obj)

    try:
        db.add_all(db_objs)
        db.commit()
        # Refreshing multiple objects requires iterating over them
        for obj in db_objs:
            db.refresh(obj)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Duplicate date trying to be entered into database.")
    
    return db_objs, True

# =================== GET Services =================== 
# These services fetch entries from the database.
async def get_assets(db: "Session", ticker: Optional[str] = None, asset_type: Optional[str] = None):
    """
    Fetch assets from the database based on ticker and/or asset type.

    Parameters:
    - db: Database session.
    - ticker: Ticker of the asset (optional).
    - asset_type: Type of the asset (optional).

    Returns:
    - List of assets that match the criteria.
    """
    if ticker:
        try:    
            return [db.query(models.Asset).filter_by(ticker=ticker).one()]
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset {ticker} not present in 'asset' table.")

    if asset_type:
        type_check = utils.asset_type(asset_type)
        if not type_check: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid asset type.")
        
        assets = db.query(models.Asset).filter_by(type=asset_type).all()
        if not assets:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No assets for given type.")
        return assets
       
async def get_bardata(db: "Session", **filter_criteria : Optional[dict]):
    """
    Fetch bar data (timeseries data) for a set of assets based on filter criteria.

    Parameters:
    - db: Database session.
    - filter_criteria: Criteria to filter the assets.

    Returns:
    - results: Dictionary with tickers as keys and corresponding bar data as values.
    """

    results = {}
    
    for ticker in filter_criteria['tickers']:
        try:    
            queried_asset = db.query(models.Asset).filter_by(ticker = ticker).one()
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset {ticker} not present in 'asset' table.")

        for asset in AssetType:
            if asset.type == queried_asset.type:
                asset_type = asset

        query = db.query(asset_type.bardata_model).filter_by(asset_id = queried_asset.asset_id)
        query = utils.apply_date_filter(query, asset_type.bardata_model, filter_criteria)
        bardata_dicts = [bardata.to_dict() for bardata in query.all()]
        results[ticker] = bardata_dicts

    return results

async def get_details(db: "Session", asset_type_str: str ,ticker: Optional[str] = None, filter_criteria: Optional[dict]= None):
    """
    Fetch asset details for a specific ticker, or set of asset based on a filter criteria.

    Parameters:
    - db: Database session.
    - asset_type_str: asset class.
    - ticker: ticker (optional)
    - filter_criteria: dictionary of the categories and the fitler values(optional)

    Returns:
    - results: List of dictionaries with the asset details.
    """
    asset_type = utils.asset_type(asset_type_str)

    query = db.query(asset_type.model)

    if ticker:
        try:    
            asset = db.query(models.Asset).filter_by(ticker = ticker).one()
        except: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset not present in 'asset' table.")
        try:
            return [query.filter_by(asset_id = asset.asset_id).one()]
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset not present in '{asset_type_str}' table.")

    query = utils.apply_filter_criteria(query=query, model = asset_type.model, filter_criteria=filter_criteria)
    results = query.all()

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No assets found with the criteria : {filter_criteria}.")

    return results
   
# DELETE Services
async def delete_asset(db: "Session", ticker: str, asset_id: int):
    """
    Delete an asset from the database using its ticker and ID.

    Parameters:
    - db: Database session.
    - ticker: Ticker of the asset.
    - asset_id: ID of the asset.

    Returns:
    - "Asset Deleted": Confirmation message.
    """
    asset = db.query(models.Asset).filter(models.Asset.ticker == ticker, models.Asset.asset_id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset with ticker {ticker} and asset_id {asset_id} not found.")

    db.delete(asset)
    db.commit()

    return f"Asset with ticker {ticker} and asset_id {asset_id} successfully deleted."

# Put Methods
async def edit_asset(db: "Session", asset_id: int, edits:dict):
    """
    Edit an asset in the database using its ID.

    Parameters:
    - db: Database session.
    - asset_id: ID of the asset.
    - edits: Dictionary containing the changes.

    Returns:
    - Modified asset.
    """

    asset_instance = db.query(models.Asset).filter_by(asset_id=asset_id).one_or_none()

    if not asset_instance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset with asset_id {asset_id} not found.")

    if 'asset_id' in edits.keys():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "Attribute 'asset_id' cannot be changed.")
    elif 'type' in edits.keys():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset 'type' cannot be changed, drop asset and re-add under correct asset class.")
    
    # Adjust ticker to new ticker
    asset_instance.ticker = edits['ticker']

    db.commit()

    return asset_instance

async def edit_asset_details(db: "Session", asset_type: str, asset_id: int, edits: dict):
    """
    Edit the details of a specific asset using its ID.

    Parameters:
    - db: Database session.
    - asset_type: The type of the asset (e.g. Equity, Bond).
    - asset_id: ID of the asset to be edited.
    - edits: Dictionary containing the attributes to be modified and their new values.

    Returns:
    - detail_instance: The modified asset details.
    """
    
    # Convert the provided asset type to the corresponding database model.
    asset_type = utils.asset_type(asset_type)

    # Check if any edits have been provided.
    if not edits:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No edits provided.")

    # Retrieve the asset instance from the database using the provided asset ID.
    asset_instance = db.query(models.Asset).filter_by(asset_id=asset_id).one_or_none()

    # If the asset instance doesn't exist, raise an error.
    if not asset_instance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset with asset_id {asset_id} not found.")
    
    # Retrieve the detailed information of the asset from the specific asset type table.
    detail_instance = utils.details_exist(db=db, ticker=asset_instance.ticker, asset_type=asset_type)

    # If the detailed information doesn't exist, raise an error.
    if not detail_instance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset with asset_id {asset_id} not found in '{asset_type.type}' table.")

    # Apply the edits to the retrieved asset details.
    for key, value in edits.items():
        if not hasattr(detail_instance, key):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"'{key}' is not a valid attribute.")
        setattr(detail_instance, key, value)

    # Commit the changes to the database.
    db.commit()

    # Return the modified asset details.
    return detail_instance

async def edit_bardata(db:"Session",  asset_type: str, asset_id: int, edits: dict):
    """
    Edit the bardata (timeseries data) of a specific asset using its ID.

    Parameters:
    - db: Database session.
    - asset_type: The type of the asset (e.g. Equity, Bond).
    - asset_id: ID of the asset whose bardata needs to be edited.
    - edits: Dictionary containing the attributes to be modified and their new values.

    Returns:
    - bardata_instance: The modified bardata.
    """
    
    # Convert the provided asset type to the corresponding database model.
    asset_type = utils.asset_type(asset_type)

    # Check if any edits have been provided.
    if not edits:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No edits provided.")
    
    # Check if 'date' attribute is provided in the correct format.
    date_value = edits.get('date')
    if not date_value or not re.match(r'^\d{4}-\d{2}-\d{2}$', date_value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"'date' attribute should be proivided in YYYY-MM-DD format.")
    
    # Retrieve the asset instance from the database using the provided asset ID.
    asset_instance = db.query(models.Asset).filter_by(asset_id=asset_id).one_or_none()

    # If the asset instance doesn't exist, raise an error.
    if not asset_instance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset with asset_id {asset_id} not found.")

    # Retrieve the bardata instance from the database using the provided asset ID, asset type, and date.
    bardata_instance = utils.get_bardata_instance(db=db, asset_id=asset_id, asset_type=asset_type, date = edits['date'])

    # If the bardata instance doesn't exist, raise an error.
    if not bardata_instance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Asset with asset_id {asset_id} not found in '{asset_type.type}_bardata' table.")
    
    # Apply the edits to the retrieved bardata.
    for key, value in edits.items():
        if not hasattr(bardata_instance, key):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"'{key}' is not a valid attribute.")
        setattr(bardata_instance, key, value)

    # Commit the changes to the database.
    db.commit()

    # Return the modified bardata.
    return bardata_instance 



   