from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from project.utils.base_model import Base


class ResumeModel(Base):
    __tablename__ = 'resume'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, server_default="nextval('resume_resume_id_seq'::regclass)")
    user_id = Column(Integer, ForeignKey('public.users.id', ondelete='CASCADE'))
    job_title = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    work_xp = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)

    def to_json(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'job_title': self.job_title,
            'education': self.education,
            'work_xp': self.work_xp,
            'skills': self.skills
        }

        return data