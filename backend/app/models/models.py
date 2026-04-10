from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

# Hier importieren wir die Base aus deiner session.py (die wir vorher erstellt haben)
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    
    # E-Mail als ID ist super für Logins!
    email = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Diese "relationships" machen es in Python super einfach, später Daten abzufragen
    paid_transactions = relationship("Transaction", back_populates="payer")
    item_splits = relationship("ItemSplit", back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Wer hat den gesamten Bon bezahlt?
    payer_email = Column(String, ForeignKey("users.email"))

    payer = relationship("User", back_populates="paid_transactions")
    items = relationship("Item", back_populates="transaction", cascade="all, delete-orphan", passive_deletes=True)


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Float, default=1.0, nullable=False) 
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    category = Column(String)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"))
    
    splits = relationship(
        "ItemSplit", 
        back_populates="item", 
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    transaction = relationship("Transaction", back_populates="items")


class ItemSplit(Base):
    __tablename__ = "item_splits"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"))
    user_email = Column(String, ForeignKey("users.email"))

    item = relationship("Item", back_populates="splits")
    user = relationship("User", back_populates="item_splits")