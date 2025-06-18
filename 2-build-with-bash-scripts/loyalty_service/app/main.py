from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Database Setup
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/loyalty_db"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)


class LoyaltyPoints(Base):
    __tablename__ = "loyalty_points"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    points = Column(Integer, default=0)


# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic models
class CustomerBase(BaseModel):
    name: str
    email: str


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int

    class Config:
        from_attributes = True


class PointsBase(BaseModel):
    points: int


class PointsResponse(BaseModel):
    customer_id: int
    points: int

    class Config:
        from_attributes = True


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Loyalty Card Service")


@app.get("/", response_model=list[CustomerResponse])
def get_all_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers


@app.post("/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = Customer(name=customer.name, email=customer.email)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    # Initialize loyalty points
    db_points = LoyaltyPoints(customer_id=db_customer.id, points=0)
    db.add(db_points)
    db.commit()

    return db_customer


@app.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/{customer_id}/points", response_model=PointsResponse)
def add_points(customer_id: int, points: PointsBase, db: Session = Depends(get_db)):
    # Validate points value
    if points.points <= 0:
        raise HTTPException(status_code=400, detail="Points must be positive")

    try:
        # Use transaction for atomic operation
        with db.begin():
            customer = db.query(Customer).get(customer_id)
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")

            loyalty_points = db.query(LoyaltyPoints).get(customer_id)
            if not loyalty_points:
                loyalty_points = LoyaltyPoints(
                    customer_id=customer_id, points=points.points
                )
                db.add(loyalty_points)
            else:
                loyalty_points.points += points.points

        db.commit()
        return {"customer_id": customer_id, "points": loyalty_points.points}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/{customer_id}/points", response_model=PointsResponse)
def get_points(customer_id: int, db: Session = Depends(get_db)):
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get loyalty points
    loyalty_points = (
        db.query(LoyaltyPoints).filter(LoyaltyPoints.customer_id == customer_id).first()
    )
    if loyalty_points is None:
        loyalty_points = LoyaltyPoints(customer_id=customer_id, points=0)
        db.add(loyalty_points)
        db.commit()
        db.refresh(loyalty_points)

    return {"customer_id": customer_id, "points": loyalty_points.points}
