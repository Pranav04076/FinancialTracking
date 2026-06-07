from sqlalchemy import Column, Integer, String, Float, Date, Enum as SAEnum, ForeignKey, UniqueConstraint
from app.db import Base
from app.schemas import TransactionType
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid = True), primary_key=True, default=uuid.uuid4)

    username = Column(String, unique=True, nullable=False)

    email = Column(String, unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key = True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable = False)
    txn_id = Column(String, unique = True, nullable=True)
    type = Column(SAEnum(TransactionType), nullable = False)
    mode = Column(String, nullable = False)
    amount = Column(Float, nullable = False)
    valueDate = Column(Date, nullable = False)
    narration = Column(String, nullable = False)
    category = Column(String, nullable = False)

class Budget(Base):
    __tablename__ ="budgets"

    id = Column(UUID(as_uuid = True), primary_key=True, default = uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable = False)
    category = Column(String, nullable = False)
    monthly_limit = Column(Float, nullable = False)

    __table_args__ = (
        UniqueConstraint("user_id", "category", name="unique_budget_per_user_category"),
    )
