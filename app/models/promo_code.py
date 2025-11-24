# app/models/promo_code.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PromoCode:
    code: str                    # FOODWEEK5832
    promo_type: str             # "week", "month"
    duration_days: int          # 7, 30
    used_by: Optional[int] = None      # user_id
    used_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    created_by: int             # admin_user_id