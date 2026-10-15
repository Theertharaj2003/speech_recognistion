from sqlalchemy import desc
from .models import QuizAttempt, QValue
ACTIONS=["review","easier","same","harder"]
ALPHA=0.25
GAMMA=0.8
def state_for(db, learner, subject):
    rows=db.query(QuizAttempt).filter_by(learner_id=learner,subject_id=subject).order_by(desc(QuizAttempt.id)).limit(5).all()
    if not rows: return "new"
    acc=sum(x.is_correct for x in rows)/len(rows)
    return "struggling" if acc<0.4 else "developing" if acc<0.8 else "mastering"
def values_for(db, learner, subject, state):
    vals={a:0.0 for a in ACTIONS}
    for row in db.query(QValue).filter_by(learner_id=learner,subject_id=subject,state=state).all(): vals[row.action]=float(row.value or 0)
    return vals
def choose(db, learner, subject, state):
    vals=values_for(db,learner,subject,state)
    if state=="new" and not any(vals.values()): return "same",vals
    return max(ACTIONS,key=lambda a:(vals[a],-ACTIONS.index(a))),vals
def update(db, learner, subject, state, action, reward, next_state):
    row=db.query(QValue).filter_by(learner_id=learner,subject_id=subject,state=state,action=action).first()
    if row is None:
        row=QValue(learner_id=learner,subject_id=subject,state=state,action=action,value=0.0); db.add(row); db.flush()
    old=float(row.value or 0)
    target=reward+GAMMA*max(values_for(db,learner,subject,next_state).values())
    row.value=old+ALPHA*(target-old)
    return row.value
