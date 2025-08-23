import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB
import pandas as pd

dotenv.load_dotenv()

STORE_ONE_CSV_PATH = "bookstore_one.csv"
STORE_TWO_CSV_PATH = "bookstore_two.csv"
DB_URI = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URI)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

def auto_cast(value: str):
    try:
        return int(value)          # try integer
    except ValueError:
        try:
            return float(value)    # try float
        except ValueError:
            return value 

class BookStoreOne(Base):
    __tablename__ = "book_store_one"
    
    id = Column(Integer, primary_key=True)
    author_name = Column(String)
    bookName = Column(String)
    stars = Column(Float)
    published_by = Column(String)
    price = Column(Float)
    
class BookStoreTwo(Base):
    __tablename__ = "book_store_two"
    
    id = Column(Integer, primary_key=True)
    rating = Column(Float)
    stock = Column(String)
    price = Column(Float)
    writer = Column(String)
    genre = Column(JSONB)
    published_by = Column(String)
    plot_summary = Column(String)
    book_title = Column(String)

Base.metadata.create_all(engine)

def main():
    df = pd.read_csv(STORE_ONE_CSV_PATH)
    df = df.where(pd.notnull(df), None)
    for i, row in df.iterrows():
        book = BookStoreOne(**row.to_dict())
        session.add(book)
    session.commit()
    print("Successfully populated book_store_one table.")

    df = pd.read_csv(STORE_TWO_CSV_PATH)
    df = df.where(pd.notnull(df), None)
    for i, row in df.iterrows():
        book = BookStoreTwo(**row.to_dict())
        session.add(book)
    session.commit()
    print("Successfully populated book_store_two table.")

if __name__ == "__main__":
    main()
