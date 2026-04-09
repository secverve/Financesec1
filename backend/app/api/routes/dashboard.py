from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import AdminDashboardSummaryResponse, UserDashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/me", response_model=UserDashboardResponse)
def get_my_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_user_dashboard(user.id)


@router.get("/admin-summary", response_model=AdminDashboardSummaryResponse)
def get_admin_summary(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return DashboardService(db).get_admin_summary()
