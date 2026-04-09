from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.order import OrderAmendRequest, OrderCreateRequest, OrderResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.get("", response_model=List[OrderResponse])
def list_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = OrderService(db).list_orders(user.id)
    return [OrderResponse.model_validate(order) for order in orders]


@router.post("", response_model=OrderResponse)
def create_order(payload: OrderCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = OrderService(db).create_order(user.id, payload)
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/amend", response_model=OrderResponse)
def amend_order(order_id: int, payload: OrderAmendRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = OrderService(db).amend_order(user.id, order_id, payload)
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = OrderService(db).cancel_order(user.id, order_id)
    return OrderResponse.model_validate(order)
