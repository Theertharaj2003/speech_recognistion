from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .database import Base, engine, get_db, SessionLocal
from .models import Subject, Lesson, Question, QuizAttempt, QValue
from .seed import seed_database
from .rl import state_for, choose, update
@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    try: seed_database(db)
    finally: db.close()
    yield
app=FastAPI(title="Adaptive Voice Learning API",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
class AnswerIn(BaseModel):
    learner_id:str=Field(default="demo-student",min_length=1,max_length=100)
    subject_id:int
    question_id:int
    selected_option:str=Field(pattern="^[ABCD]$")
@app.get("/")
def root(): return {"name":"Adaptive Voice Learning API","version":"1.0.0","docs":"/docs"}
@app.get("/api/health")
def health(): return {"status":"ok"}
@app.get("/api/subjects")
def subjects(db:Session=Depends(get_db)): return db.query(Subject).order_by(Subject.id).all()
@app.get("/api/subjects/{sid}/lessons")
def lessons(sid:int,db:Session=Depends(get_db)):
    if not db.query(Subject).filter_by(id=sid).first(): raise HTTPException(404,"Subject not found")
    return db.query(Lesson).filter_by(subject_id=sid).order_by(Lesson.difficulty).all()
@app.get("/api/subjects/{sid}/questions")
def questions(sid:int,difficulty:int|None=Query(default=None,ge=1,le=3),db:Session=Depends(get_db)):
    if not db.query(Subject).filter_by(id=sid).first(): raise HTTPException(404,"Subject not found")
    q=db.query(Question).filter_by(subject_id=sid)
    if difficulty is not None:
        lids=[x.id for x in db.query(Lesson).filter_by(subject_id=sid,difficulty=difficulty).all()]
        q=q.filter(Question.lesson_id.in_(lids))
    rows=q.order_by(Question.id).all()
    return [{"id":x.id,"subject_id":x.subject_id,"lesson_id":x.lesson_id,"prompt":x.prompt,"option_a":x.option_a,"option_b":x.option_b,"option_c":x.option_c,"option_d":x.option_d} for x in rows]
@app.get("/api/lessons/{lid}")
def lesson(lid:int,db:Session=Depends(get_db)):
    x=db.query(Lesson).filter_by(id=lid).first()
    if not x: raise HTTPException(404,"Lesson not found")
    return x
def rec_data(db, learner, sid):
    state=state_for(db,learner,sid); action,vals=choose(db,learner,sid,state)
    latest=db.query(QuizAttempt).filter_by(learner_id=learner,subject_id=sid).order_by(desc(QuizAttempt.id)).first()
    difficulty=latest.difficulty if latest else 1
    target=max(1,difficulty-1) if action=="easier" else min(3,difficulty+1) if action=="harder" else difficulty
    rationale={"review":"Review the current topic to strengthen retention.","easier":"Recent answers suggest practising a simpler lesson.","same":"Continue at this level while collecting more evidence.","harder":"Try a more challenging lesson based on reward history."}[action]
    return {"subject_id":sid,"learner_id":learner,"state":state,"action":action,"target_difficulty":target,"rationale":rationale,"q_values":vals}
@app.post("/api/quiz/answer")
def answer(p:AnswerIn,db:Session=Depends(get_db)):
    q=db.query(Question).filter_by(id=p.question_id,subject_id=p.subject_id).first()
    if not q or not db.query(Subject).filter_by(id=p.subject_id).first(): raise HTTPException(404,"Subject or question not found")
    before=state_for(db,p.learner_id,p.subject_id); correct=p.selected_option==q.correct_option
    l=db.query(Lesson).filter_by(id=q.lesson_id).first()
    attempt=QuizAttempt(learner_id=p.learner_id,subject_id=p.subject_id,question_id=q.id,selected_option=p.selected_option,is_correct=int(correct),difficulty=l.difficulty if l else 1)
    db.add(attempt); db.flush()
    after=state_for(db,p.learner_id,p.subject_id)
    action,_=choose(db,p.learner_id,p.subject_id,before)
    reward=1.0 if correct else -1.0
    update(db,p.learner_id,p.subject_id,before,action,reward,after); db.commit()
    return {"id":attempt.id,"learner_id":p.learner_id,"subject_id":p.subject_id,"question_id":q.id,"selected_option":p.selected_option,"is_correct":correct,"explanation":q.explanation,"reward":reward,"recommended_action":rec_data(db,p.learner_id,p.subject_id)["action"]}
@app.get("/api/recommendations/{sid}")
def recommendation(sid:int,learner_id:str="demo-student",db:Session=Depends(get_db)):
    if not db.query(Subject).filter_by(id=sid).first(): raise HTTPException(404,"Subject not found")
    return rec_data(db,learner_id,sid)
@app.get("/api/analytics")
def analytics(learner_id:str="demo-student",db:Session=Depends(get_db)):
    rows=db.query(QuizAttempt).filter_by(learner_id=learner_id).order_by(QuizAttempt.id).all()
    correct=sum(x.is_correct for x in rows); recent=rows[-10:]
    groups=[]
    for s in db.query(Subject).order_by(Subject.id).all():
        r=[x for x in rows if x.subject_id==s.id]; c=sum(x.is_correct for x in r)
        groups.append({"subject_id":s.id,"subject":s.name,"attempts":len(r),"correct":c,"accuracy_percent":round(c/len(r)*100,1) if r else 0})
    return {"learner_id":learner_id,"total_attempts":len(rows),"correct_answers":correct,"accuracy_percent":round(correct/len(rows)*100,1) if rows else 0,"average_recent_accuracy":round(sum(x.is_correct for x in recent)/len(recent)*100,1) if recent else 0,"subjects":groups,"engagement_sessions":len({x.created_at.date().isoformat() for x in rows})}
@app.get("/api/history")
def history(learner_id:str="demo-student",limit:int=Query(default=30,ge=1,le=200),db:Session=Depends(get_db)):
    rows=db.query(QuizAttempt).filter_by(learner_id=learner_id).order_by(desc(QuizAttempt.id)).limit(limit).all(); out=[]
    for a in rows:
        q=db.query(Question).filter_by(id=a.question_id).first(); s=db.query(Subject).filter_by(id=a.subject_id).first()
        out.append({"id":a.id,"subject":s.name if s else "Unknown","question":q.prompt if q else "Deleted question","selected_option":a.selected_option,"is_correct":bool(a.is_correct),"created_at":a.created_at.isoformat()})
    return out
@app.get("/api/evaluation/baseline")
def evaluation(subject_id:int,learner_id:str="demo-student",db:Session=Depends(get_db)):
    rows=db.query(QuizAttempt).filter_by(learner_id=learner_id,subject_id=subject_id).order_by(QuizAttempt.id).all()
    mid=max(1,len(rows)//2); first,second=rows[:mid],rows[mid:]
    def acc(group): return round(sum(x.is_correct for x in group)/len(group)*100,1) if group else None
    return {"subject_id":subject_id,"early_attempt_accuracy_percent":acc(first),"later_attempt_accuracy_percent":acc(second),"attempts":len(rows),"note":"Descriptive comparison only; it does not prove causation."}
@app.delete("/api/demo/reset")
def reset(learner_id:str="demo-student",db:Session=Depends(get_db)):
    db.query(QuizAttempt).filter_by(learner_id=learner_id).delete(); db.query(QValue).filter_by(learner_id=learner_id).delete(); db.commit()
    return {"status":"reset","learner_id":learner_id}
