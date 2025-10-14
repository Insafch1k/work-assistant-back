from typing import Optional
from pydantic import BaseModel, ConfigDict


class Resume(BaseModel):
    id: int
    user_id: int
    job_title: Optional[str] = None
    education: Optional[str] = None
    work_xp: Optional[str] = None
    skills: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    def to_json(self):
        data = {
            'job_title': self.job_title,
            'education': self.education,
            'work_xp': self.work_xp,
            'skills': self.skills
        }

        return data