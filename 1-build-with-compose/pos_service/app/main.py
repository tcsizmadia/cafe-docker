from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import List, Dict, Optional
from httpx import AsyncClient, Timeout
from tenacity import retry, stop_after_attempt, wait_exponential

# Database Setup
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/pos_db"
)
LOYALTY_SERVICE_URL = os.getenv("LOYALTY_SERVICE_URL", "http://localhost:8001")
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://localhost:8002")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=True)  # Can be null for guests
    items = Column(JSON)  # Store items as JSON
    total_price = Column(Float)


# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic models
class TransactionItem(BaseModel):
    item_id: int
    quantity: int


class TransactionBase(BaseModel):
    customer_id: Optional[int] = None
    items: List[TransactionItem]


class TransactionResponse(BaseModel):
    id: int
    customer_id: Optional[int]
    items: List[Dict]
    total_price: float

    class Config:
        from_attributes = True


class LoyaltyApplyRequest(BaseModel):
    points_to_use: int


# Dependency
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, max=10))
def get_db_connection():
    db = SessionLocal()
    try:
        # Test the connection
        db.execute(text("SELECT 1")).fetchone()
        return db
    except Exception as e:
        db.close()
        raise e


def get_db():
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="POS Integration Service")


@app.get("/", response_model=List[TransactionResponse])
def get_all_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions


@app.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionBase, db: Session = Depends(get_db)
):
    timeout = Timeout(5.0, read=5.0, write=5.0, connect=5.0)

    async with AsyncClient(timeout=timeout) as client:
        # Validate customer if provided
        if transaction.customer_id is not None:
            try:
                response = await client.get(
                    f"{LOYALTY_SERVICE_URL}/{transaction.customer_id}"
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=404, detail="Customer not found in loyalty system"
                    )
            except Exception:
                # Just log this error but don't fail the transaction
                print(
                    f"Warning: Could not validate customer {transaction.customer_id} with loyalty service"
                )

        # Validate and fetch items from menu service
        item_details = []
        total_price = 0.0

        for item in transaction.items:
            try:
                response = await client.get(f"{MENU_SERVICE_URL}/{item.item_id}")
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=404, detail=f"Menu item {item.item_id} not found"
                    )

                menu_item = response.json()
                item_price = menu_item["price"] * item.quantity
                total_price += item_price

                item_details.append(
                    {
                        "item_id": item.item_id,
                        "name": menu_item["name"],
                        "quantity": item.quantity,
                        "unit_price": menu_item["price"],
                        "total_price": item_price,
                    }
                )
            except Exception:
                # Log this error but continue with the next item
                print(
                    f"Warning: Could not fetch menu item {item.item_id} from menu service"
                )

        # Create transaction record
        db_transaction = Transaction(
            customer_id=transaction.customer_id,
            items=item_details,
            total_price=total_price,
        )

        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)

        # If customer is provided, add loyalty points (1 point per dollar spent)
        if transaction.customer_id is not None:
            try:
                points_to_add = int(total_price)  # Convert to integer points
                if points_to_add > 0:
                    await client.post(
                        f"{LOYALTY_SERVICE_URL}/{transaction.customer_id}/points",
                        json={"points": points_to_add},
                    )
            except Exception:
                # Just log this error but don't fail the transaction
                print(
                    f"Warning: Could not add loyalty points for customer {transaction.customer_id}"
                )

        return db_transaction


@app.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/{transaction_id}/apply_loyalty")
async def apply_loyalty_points(
    transaction_id: int, request: LoyaltyApplyRequest, db: Session = Depends(get_db)
):
    # Get transaction
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.customer_id is None:
        raise HTTPException(
            status_code=400, detail="Transaction has no associated customer"
        )

    timeout = Timeout(5.0, read=5.0, write=5.0, connect=5.0)
    async with AsyncClient(timeout=timeout) as client:
        # Check if customer has enough points
        try:
            response = await client.get(
                f"{LOYALTY_SERVICE_URL}/{transaction.customer_id}/points"
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=404, detail="Could not retrieve loyalty points"
                )

            loyalty_data = response.json()
            available_points = loyalty_data["points"]

            if available_points < request.points_to_use:
                raise HTTPException(
                    status_code=400,
                    detail=f"Customer only has {available_points} points available",
                )

            # Calculate discount (1 point = $0.10 off)
            discount_value = request.points_to_use * 0.1
            new_total = max(0, transaction.total_price - discount_value)

            # Update transaction
            transaction.total_price = new_total
            db.commit()

            # Deduct points from loyalty system
            await client.post(
                f"{LOYALTY_SERVICE_URL}/{transaction.customer_id}/points",
                json={"points": -request.points_to_use},
            )

            return {
                "transaction_id": transaction_id,
                "points_used": request.points_to_use,
                "discount_applied": discount_value,
                "new_total": new_total,
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error communicating with loyalty service: {str(e)}",
            )
