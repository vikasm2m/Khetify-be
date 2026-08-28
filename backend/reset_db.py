import os
import sys
from sqlalchemy import create_engine, MetaData

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)
metadata.drop_all(bind=engine)

print("Database cleared.")
