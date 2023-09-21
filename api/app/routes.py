from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from sqlalchemy.orm import Session
import app.schemas as schemas
import services.services as services
from typing import Optional, List, Dict
from database import utils as database_utils

router = APIRouter()

# =================== ADMIN ENDPOINTS ===================

# Endpoint to construct database tables
@router.post("/api/database/")
def create_tables():
    """Creates necessary database tables."""
    database_utils._create_tables()

# Endpoint to delete database tables
@router.delete("/api/database/")
def delete_tables():
    """Deletes the specified database tables."""
    database_utils._delete_tables()

# =================== ASSET CRUD OPERATIONS ===================

# Endpoint to create a new asset
@router.post("/api/asset/", response_model=schemas.RetrieveAsset)
async def create_asset_endpoint(asset: schemas.CreateAsset, db: Session = Depends(database_utils._get_db)):
    """Creates a new asset entry in the database."""
    result, success = await services.create_asset(db=db, asset=asset)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
    return result

# Endpoint to retrieve assets based on filters
@router.get("/api/asset/", response_model=List[schemas.RetrieveAsset])
async def get_asset(ticker: Optional[str] = None, asset_type: Optional[str] = None, db: Session = Depends(database_utils._get_db)):
    """Retrieves assets from the database based on provided filters."""
    return await services.get_assets(db=db, ticker=ticker, asset_type=asset_type)

# Endpoint to delete an asset
@router.delete("/api/asset/")
async def delete_asset(ticker: str, asset_id: int, db: Session = Depends(database_utils._get_db)):
    """Deletes an asset entry from the database."""
    return await services.delete_asset(db=db, ticker=ticker, asset_id=asset_id)

# Endpoint to edit an asset's details
@router.put("/api/asset/{asset_id}", response_model=schemas.RetrieveAsset)
async def edit_asset(asset_id: int, edits: dict, db: Session = Depends(database_utils._get_db)):
    """Updates an asset's details in the database."""
    return await services.edit_asset(db=db, asset_id=asset_id, edits=edits)

# =================== ASSET DETAILS CRUD OPERATIONS ===================

# Function to generate endpoint for creating asset details
def create_asset_details_endpoint(asset_type, create_schema, retrieve_schema):
    """Generates an endpoint for creating asset details."""
    @router.post(f"/api/{asset_type}/{{ticker}}/", response_model=retrieve_schema)
    async def create_asset_details(data: create_schema, ticker: str = Path(...), db: Session = Depends(database_utils._get_db)):
        result, success = await services.add_details(db=db, ticker=ticker, asset_type=asset_type, data=data)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
        return result

# Function to generate endpoints for retrieving asset details
def get_details_endpoint(asset_type, retrieve_schema):
    """Generates endpoints for retrieving asset details."""
    @router.get(f"/api/{asset_type}/{{ticker}}", response_model=List[retrieve_schema])
    async def get_details_by_ticker(ticker: str, db: Session = Depends(database_utils._get_db)):
        return await services.get_details(db=db, asset_type_str=asset_type, ticker=ticker)

    @router.post(f"/api/{asset_type}", response_model=List[retrieve_schema])
    async def get_details_by_filter(criteria: dict, db: Session = Depends(database_utils._get_db)):
        return await services.get_details(db=db, asset_type_str=asset_type, filter_criteria=criteria)

# Function to generate endpoints for editing asset details
def edit_asset_details_endpoint(asset_type, retrieve_schema):
    """Generates an endpoint for editing asset details."""
    @router.put(f"/api/{asset_type}/{{asset_id}}", response_model=retrieve_schema)
    async def edit_asset_details(asset_id: int, edits: dict, db: Session = Depends(database_utils._get_db)):
        return await services.edit_asset_details(db=db, asset_type=asset_type, asset_id=asset_id, edits=edits)

# =================== ASSET BAR DATA CRUD OPERATIONS ===================

# Function to generate endpoint for creating bardata
def create_bardata_endpoint_router(asset_type):
    """Generates an endpoint for creating bardata."""
    @router.post(f"/api/{asset_type}/{{ticker}}/bardata/", response_model=List[schemas.RetrieveBardata])
    async def create_bardata(data: List[schemas.CreateBardata], ticker: str = Path(...), db: Session = Depends(database_utils._get_db)):
        result, success = await services.add_bardata(db=db, ticker=ticker, asset_type=asset_type, data=data)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
        return result

# Endpoint to retrieve bardata based on filters
@router.post("/api/bardata/", response_model=Dict[str, List[schemas.RetrieveBardata]])
async def get_bardata(criteria: schemas.BardataFilter = Body(...), db: Session = Depends(database_utils._get_db)):
    """Retrieves bardata based on provided criteria."""
    return await services.get_bardata(db=db, **criteria.dict())

# Function to generate endpoints for editing bardata
def edit_bardata_endpoint(asset_type):
    """Generates an endpoint for editing bardata."""
    @router.put(f"/api/{asset_type}/bardata/{{asset_id}}", response_model=schemas.RetrieveBardata)
    async def edit_bardata(asset_id: int, edits: dict, db: Session = Depends(database_utils._get_db)):
        return await services.edit_bardata(db=db, asset_type=asset_type, asset_id=asset_id, edits=edits)

# =================== CREATE ENDPOINTS BASED ON SCHEMAS ===================

create_asset_details_endpoint('equity', schemas.CreateEquity, schemas.RetrieveEquity)
create_asset_details_endpoint('cryptocurrency', schemas.CreateCryptocurrency, schemas.RetrieveCryptocurrency)
create_asset_details_endpoint('commodityfuture', schemas.CreateCommodityFuture, schemas.RetrieveCommodityFuture)

create_bardata_endpoint_router('equity')
create_bardata_endpoint_router('cryptocurrency')
create_bardata_endpoint_router('commodityfuture')

get_details_endpoint('equity', schemas.RetrieveEquity)
get_details_endpoint('commodityfuture', schemas.RetrieveCommodityFuture)
get_details_endpoint('cryptocurrency', schemas.RetrieveCryptocurrency)

edit_asset_details_endpoint('equity', schemas.RetrieveEquity)
edit_asset_details_endpoint('cryptocurrency', schemas.RetrieveCryptocurrency)
edit_asset_details_endpoint('commodityfuture', schemas.RetrieveCommodityFuture)

edit_bardata_endpoint('equity')
edit_bardata_endpoint('cryptocurrency')
edit_bardata_endpoint('commodityfuture')
