from sqlalchemy import Column, String, DateTime, Integer, Float, LargeBinary, text
from .base import Base

SCHEMA = "metrics"

class RouteMetrics(Base):
    __tablename__ = "route_metrics"
    __table_args__ = {"schema": SCHEMA}
    time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), primary_key=True)
    route = Column(String, nullable=False, primary_key=True)
    requests = Column(Integer, nullable=False)
    avg_response_time = Column(Float)
    min_response_time = Column(Float)
    max_response_time = Column(Float)
    p50 = Column(Float)
    p95 = Column(Float)
    p99 = Column(Float)
    tdigest = Column(LargeBinary)

class RouteStatusCodes(Base):
    __tablename__ = "route_status_codes"
    __table_args__ = {"schema": SCHEMA}
    time = Column(DateTime, nullable=False, primary_key=True)
    route = Column(String, nullable=False, primary_key=True)
    status_code = Column(Integer, nullable=False, primary_key=True)
    count = Column(Integer, nullable=False)

class GlobalMetrics(Base):
    __tablename__ = "global_metrics"
    __table_args__ = {"schema": SCHEMA}
    time = Column(DateTime, primary_key=True)
    total_requests = Column(Integer)
    avg_response_time = Column(Float)
    error_rate = Column(Float)