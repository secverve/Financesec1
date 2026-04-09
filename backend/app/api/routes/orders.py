from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.order import OrderCreateRequest, OrderResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.post("", response_model=OrderResponse)
def create_order(payload: OrderCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = OrderService(db).create_order(user.id, payload)
    return OrderResponse.model_validate(order)
