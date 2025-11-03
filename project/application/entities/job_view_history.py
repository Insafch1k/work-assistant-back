from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
class JobViewHistory(BaseModel):
    id: int
    user_id: int
    job_id: int
    viewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    def to_json(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'viewed_at': self.viewed_at.strftime("%d-%m-%Y %H:%M:%S") if self.viewed_at else None
        }
        return data