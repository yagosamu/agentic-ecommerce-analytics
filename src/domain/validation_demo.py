import uuid
import sys
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domain.models import Order, Review

order_id = uuid.uuid4()
customer_id = uuid.uuid4()
product_id = uuid.uuid4()
order_id_2 = uuid.uuid4()

# 1. Valid Order
print("=== 1. Order valida ===")
order = Order(
    order_id=order_id,
    customer_id=customer_id,
    product_id=product_id,
    qty=3,
    total=299.90,
    status="delivered",
    payment="pix",
    created_at=datetime.now(),
)
print(order)
print()

# 2. Order com qty=0 — deve falhar
print("=== 2. Order com qty=0 ===")
try:
    Order(
        order_id=uuid.uuid4(),
        customer_id=customer_id,
        product_id=product_id,
        qty=0,
        total=100.0,
        status="shipped",
        payment="credit_card",
    )
except ValidationError as e:
    print(f"ERRO: {e.errors()[0]['msg']}")
print()

# 3. Order com payment='dinheiro' — deve falhar
print("=== 3. Order com payment='dinheiro' ===")
try:
    Order(
        order_id=uuid.uuid4(),
        customer_id=customer_id,
        product_id=product_id,
        qty=1,
        total=50.0,
        status="processing",
        payment="dinheiro",
    )
except ValidationError as e:
    print(f"ERRO: {e.errors()[0]['msg']}")
print()

# 4. Valid Review com rating=5
print("=== 4. Review valida (rating=5) ===")
review = Review(
    review_id=uuid.uuid4(),
    order_id=order_id,
    rating=5,
    comment="Produto chegou antes do prazo, estou muito satisfeito.",
    sentiment="positive",
)
print(review)
print()

# 5. Review com rating=6 — deve falhar
print("=== 5. Review com rating=6 ===")
try:
    Review(
        review_id=uuid.uuid4(),
        order_id=order_id,
        rating=6,
        comment="Pessimo.",
        sentiment="negative",
    )
except ValidationError as e:
    print(f"ERRO: {e.errors()[0]['msg']}")
