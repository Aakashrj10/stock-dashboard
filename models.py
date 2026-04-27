from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class StockData(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    data = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    daily_return = Column(Float)
    moving_avg_7d = Column(Float)
    week_52_low = Column(Float)
    week_52_high = Column(Float)