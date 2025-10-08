from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from project.utils.base_model import Base


class Resume(Base):
    __tablename__ = 'resume'
    __table_args__ = {'schema': 'public'}

    resume_id = Column(Integer, primary_key=True, server_default="nextval('resume_resume_id_seq'::regclass)")
    user_id = Column(Integer, ForeignKey('public.finders.user_id', ondelete='CASCADE'))
    job_title = Column(Text, nullable=False)
    education = Column(Text, nullable=False)
    work_xp = Column(Text, nullable=False)
    skills = Column(Text, nullable=False)

    # Опционально: связь с таблицей finders
    finder = relationship("Finder", back_populates="resumes")

    def to_json(self):
        data = {
            'resume_id': self.resume_id,
            'user_id': self.user_id,
            'job_title': self.job_title,
            'education': self.education,
            'work_xp': self.work_xp,
            'skills': self.skills
        }

        return data