from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
class JobFavorite(BaseModel):
    id: int
    user_id: int
    job_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    def to_json(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        return data