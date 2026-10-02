from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Neon suspends idle compute and drops open connections. pool_pre_ping swaps out
# a dead pooled connection before use (otherwise the first request after idle
# fails with "SSL SYSCALL error: EOF"); pool_recycle retires old connections.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
