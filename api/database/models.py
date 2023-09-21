from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, BigInteger, func
from sqlalchemy.orm import relationship, declarative_base
import sqlalchemy

Base = declarative_base()

# Asset Models
class Asset(Base):
    __tablename__ = 'asset'
    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, unique=True)
    type = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (sqlalchemy.UniqueConstraint('ticker', 'type', name='uix_ticker_type'),)
    
    # Add cascade option
    equity = relationship('Equity', back_populates='asset', cascade="all, delete-orphan")
    commodity_future = relationship('CommodityFuture', back_populates='asset', cascade="all, delete-orphan")
    cryptocurrency = relationship('Cryptocurrency', back_populates='asset', cascade="all, delete-orphan")
    equity_bardata = relationship('EquityBarData', back_populates='asset', cascade="all, delete-orphan")
    commodity_future_bardata = relationship('CommodityFutureBarData', back_populates='asset', cascade="all, delete-orphan")
    cryptocurrency_bardata = relationship('CryptocurrencyBarData', back_populates='asset', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'asset_id':self.asset_id,
            'ticker':self.ticker, 
            'type':self.type
        }

    def __repr__(self):
        return f"Asset :\n asset_id = {self.asset_id}\n ticker = {self.ticker}\n type = {self.type}"
    
# Equity Models
class Equity(Base):
    __tablename__ = 'equity'
    equity_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey('asset.asset_id'), nullable=False)
    asset = relationship('Asset', back_populates='equity')
    company_name = Column(String(150), nullable=False)
    exchange = Column(String(25), nullable=False)
    currency = Column(String(3))
    industry = Column(String(50), default='NUll')
    description = Column(String(1000))
    market_cap = Column(Integer)
    shares_outstanding = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert the Equity object to a dictionary."""
        return {
            'equity_id': self.equity_id,
            'asset_id': self.asset_id,
            'company_name': self.company_name,
            'exchange': self.exchange,
            'currency': self.currency,
            'industry': self.industry,
            'description': self.description,
            'market_cap': self.market_cap,
            'shares_outstanding': self.shares_outstanding
        }

    def __repr__(self):
        return f"Equity :\n equity_id = {self.equity_id}\n asset_id = {self.asset_id}\n company = {self.company_name}\n exchange = {self.exchange}\n currency = {self.currency}\n industry = {self.industry}\n market_cap = {self.market_cap}\n shares_outstanding = {self.shares_outstanding}\n description = {self.description}"

class EquityBarData(Base):
    __tablename__ = 'equity_bardata' 
    record_id = Column(Integer,primary_key = True, autoincrement=True)  
    asset_id = Column(Integer, ForeignKey('asset.asset_id'), nullable=False)
    asset = relationship('Asset', back_populates='equity_bardata')
    date = Column(DateTime, nullable=False)
    open = Column(DECIMAL(10,2))
    close = Column(DECIMAL(10,2))
    high = Column(DECIMAL(10,2))
    low = Column(DECIMAL(10,2))
    volume = Column(BigInteger)
    adjusted_close = Column(DECIMAL(10,2))

    __table_args__ = (sqlalchemy.UniqueConstraint('asset_id', 'date', name='uix_equity_bardata_asset_id_date'),)

    def get_date(self):
        return self.date

    def to_dict(self):
        return {
            'record_id': self.record_id,
            'asset_id': self.asset_id,
            'date': self.date,
            'open': float(self.open) if self.open else None,
            'close': float(self.close) if self.close else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'volume': self.volume,
            'adjusted_close': float(self.adjusted_close) if self.adjusted_close else None
        }

    def __repr__(self):
        return f"<EquityBarData(record_id={self.record_id}, asset_id={self.asset_id}, date={self.date}, open={self.open}, close={self.close}, high={self.high}, low={self.low}, volume={self.volume}, adjusted_close={self.adjusted_close})>"

# Commodity Futures Models
class CommodityFuture(Base):
    __tablename__ = 'commodity_future'
    commodity_future_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey('asset.asset_id'), nullable=False)
    asset = relationship('Asset', back_populates='commodity_future')
    commodity_name = Column(String(25), nullable=False)
    base_future_code = Column(String(10), nullable=False)
    expiration_date = Column(DateTime, nullable=False)  # Added this line
    industry = Column(String(50), default='NUll')
    exchange = Column(String(25))
    currency = Column(String(3))
    description = Column(String(1000))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


    def to_dict(self):
        return {
            'commodity_future_id': self.commodity_future_id,
            'asset_id': self.asset_id,
            'commodity_name': self.commodity_name,
            'base_future_code': self.base_future_code,
            'expiration_date': self.expiration_date,
            'industry': self.industry,
            'exchange': self.exchange,
            'currency': self.currency,
            'description': self.description
        }

    def __repr__(self):
        return f"Commodity Future :\n commodity_future_id = {self.commodity_future_id}\n asset_id = {self.asset_id}\n commodity_name = {self.commodity_name}\n base_future_code = {self.base_future_code}\n expiration_date = {self.expiration_date}\n industry = {self.industry}\n exchange = {self.exchange}\n currency = {self.currency}\n description = {self.description}"

class CommodityFutureBarData(Base):
    __tablename__ = 'commodity_future_bardata' 
    record_id = Column(Integer,primary_key = True, autoincrement=True)  
    asset_id = Column(Integer, ForeignKey('asset.asset_id'), nullable=False)
    asset = relationship('Asset', back_populates='commodity_future_bardata')
    date = Column(DateTime, nullable=False)
    open = Column(DECIMAL(10,2))
    close = Column(DECIMAL(10,2))
    high = Column(DECIMAL(10,2))
    low = Column(DECIMAL(10,2))
    volume = Column(BigInteger)

    __table_args__ = (sqlalchemy.UniqueConstraint('asset_id', 'date', name='uix_commodidty_future_bardata_asset_id_date'),)

    def to_dict(self):
        return {
            'record_id': self.record_id,
            'asset_id': self.asset_id,
            'date': self.date,
            'open': float(self.open) if self.open else None,
            'close': float(self.close) if self.close else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'volume': self.volume
        }

    def __repr__(self):
        return f"<CommodityFutureBarData(record_id={self.record_id}, asset_id={self.asset_id}, date={self.date}, open={self.open}, close={self.close}, high={self.high}, low={self.low}, volume={self.volume})>"

# Cryptocurrency Models
class Cryptocurrency(Base):
    __tablename__ = "cryptocurrency"
    cryptocurrency_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey('asset.asset_id'), nullable=False)
    asset = relationship('Asset', back_populates='cryptocurrency')
    cryptocurrency_name = Column(String(50), nullable=False)  # Specified length
    circulating_supply = Column(Integer)
    market_cap = Column(Integer)
    total_supply = Column(Integer)
    max_supply = Column(Integer)
    description = Column(String(1000))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'cryptocurrency_id': self.cryptocurrency_id,
            'asset_id': self.asset_id,
            'cryptocurrency_name': self.cryptocurrency_name,
            'circulating_supply': self.circulating_supply,
            'market_cap': self.market_cap,
            'total_supply': self.total_supply,
            'max_supply': self.max_supply,
            'description': self.description
        }

    def __repr__(self):
        return f"CRYPTOCURRENCY :\n cryptocurrency_id = {self.cryptocurrency_id}\n asset_id = {self.asset_id}\n cryptocurrency_name = {self.cryptocurrency_name}\n circulating_supply = {self.circulating_supply}\n market_cap = {self.market_cap}\n total_supply = {self.total_supply}\n max_supply = {self.max_supply}\n description = {self.description}"
    
class CryptocurrencyBarData(Base):
    __tablename__ = 'cryptocurrency_bardata' 
    record_id = Column(Integer,primary_key = True, autoincrement=True)  
    asset_id = Column(Integer, ForeignKey('asset.asset_id'), nullable=False)
    asset = relationship('Asset', back_populates='cryptocurrency_bardata')
    date = Column(DateTime, nullable=False)
    open = Column(DECIMAL(10,2))
    close = Column(DECIMAL(10,2))
    high = Column(DECIMAL(10,2))
    low = Column(DECIMAL(10,2))
    volume = Column(BigInteger)

    __table_args__ = (sqlalchemy.UniqueConstraint('asset_id', 'date', name='uix_cryptocurrency_bardata_asset_id_date'),)


    def to_dict(self):
        return {
            'record_id': self.record_id,
            'asset_id': self.asset_id,
            'date': self.date,
            'open': float(self.open) if self.open else None,
            'close': float(self.close) if self.close else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'volume': self.volume
        }

    def __repr__(self):
        return f"<CryptocurrencyBarData(record_id={self.record_id}, asset_id={self.asset_id}, date={self.date}, open={self.open}, close={self.close}, high={self.high}, low={self.low}, volume={self.volume})>"
