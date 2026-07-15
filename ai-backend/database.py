import os
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. Set it in your .env file, "
        "e.g. mysql+pymysql://user:password@host:3306/dbname"
    )

# pool_pre_ping: issues a lightweight SELECT 1 before handing out a pooled
# connection, so connections MySQL has silently dropped (idle timeout) are
# detected and replaced instead of causing a random 500 mid-request.
# pool_recycle: proactively recycles connections before MySQL's own
# wait_timeout (commonly 28800s, but can be much lower on managed hosts)
# closes them from the server side.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=280,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Define our database table
class InteractionRecord(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), index=True)
    # Storing the complex form state as a JSON column keeps our schema flexible and clean
    interaction_data = Column(JSON)


# This automatically creates the table in your MySQL database when the server starts
Base.metadata.create_all(bind=engine)