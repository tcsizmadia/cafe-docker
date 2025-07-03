from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import List
import time

# Database Setup
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/menu_db"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)


# Create tables
Base.metadata.create_all(bind=engine)


# Seed some data for demo purposes
def seed_menu_data():
    db = SessionLocal()

    # Check if we already have menu items
    existing_items = db.query(MenuItem).count()
    if existing_items == 0:
        # Add sample menu items
        sample_items = [
            MenuItem(
                name="Espresso",
                description="Strong coffee brewed by forcing hot water under pressure through finely ground coffee beans",
                price=2.50,
            ),
            MenuItem(
                name="Cappuccino",
                description="Coffee drink topped with foamed milk",
                price=3.50,
            ),
            MenuItem(name="Latte", description="Coffee with steamed milk", price=4.00),
            MenuItem(name="Croissant", description="Buttery, flaky pastry", price=2.75),
            MenuItem(
                name="Avocado Toast",
                description="Toast topped with avocado, salt, and pepper",
                price=6.50,
            ),
        ]

        db.add_all(sample_items)
        db.commit()

    db.close()


# Pydantic models
class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemResponse(MenuItemBase):
    id: int

    class Config:
        from_attributes = True


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Menu Service")


@app.on_event("startup")
async def startup_event():
    max_retries = 5
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            seed_menu_data()
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("Failed to connect to database after maximum retries")
                raise


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/", response_model=List[MenuItemResponse])
def get_menu(db: Session = Depends(get_db)):
    menu_items = db.query(MenuItem).all()
    return menu_items


@app.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item
