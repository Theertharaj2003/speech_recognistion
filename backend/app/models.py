from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from .database import Base
class Subject(Base):
    __tablename__="subjects"
    id=Column(Integer, primary_key=True)
    name=Column(String(100), nullable=False)
    description=Column(Text, default="")
class Lesson(Base):
    __tablename__="lessons"
    id=Column(Integer, primary_key=True)
    subject_id=Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title=Column(String(160), nullable=False)
    difficulty=Column(Integer, default=1)
    content=Column(Text, nullable=False)
class Question(Base):
    __tablename__="questions"
    id=Column(Integer, primary_key=True)
    subject_id=Column(Integer, ForeignKey("subjects.id"), nullable=False)
    lesson_id=Column(Integer, ForeignKey("lessons.id"))
    prompt=Column(Text, nullable=False)
    option_a=Column(String(250), nullable=False)
    option_b=Column(String(250), nullable=False)
    option_c=Column(String(250), nullable=False)
    option_d=Column(String(250), nullable=False)
    correct_option=Column(String(1), nullable=False)
    explanation=Column(Text, default="")
class QuizAttempt(Base):
    __tablename__="quiz_attempts"
    id=Column(Integer, primary_key=True)
    learner_id=Column(String(100), index=True, default="demo-student")
    subject_id=Column(Integer, ForeignKey("subjects.id"), nullable=False)
    question_id=Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option=Column(String(1), nullable=False)
    is_correct=Column(Integer, nullable=False)
    difficulty=Column(Integer, default=1)
    created_at=Column(DateTime, default=datetime.utcnow, nullable=False)
class QValue(Base):
    __tablename__="q_values"
    id=Column(Integer, primary_key=True)
    learner_id=Column(String(100), index=True, nullable=False)
    subject_id=Column(Integer, ForeignKey("subjects.id"), index=True, nullable=False)
    state=Column(String(40), nullable=False)
    action=Column(String(40), nullable=False)
    value=Column(Float, default=0.0)
