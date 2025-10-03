from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class Policy(BaseModel):
    id: int
    customer_id: int
    start_date: date
    end_date: date
    product: str
    premium: Decimal