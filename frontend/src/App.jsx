import React,{useEffect,useState}from'react';import{Activity,AudioLines,BookOpen,BrainCircuit,CheckCircle2,ChevronRight,Languages,Mic,RotateCcw,Volume2,XCircle}from'lucide-react';import{Bar,BarChart,CartesianGrid,ResponsiveContainer,Tooltip,XAxis,YAxis}from'recharts';import{api}from'./api';
const words={en:{dashboard:'Dashboard',learn:'Learn',analytics:'Analytics',welcome:'Learn in your own voice.',start:'Start learning',subjects:'Your learning paths',language:'Language',lesson:'Lesson',quiz:'Quick check',submit:'Check answer',next:'Next question',speak:'Speak option',correct:'Correct answer!',wrong:'Not quite. Review the explanation.',recommend:'Adaptive recommendation',reset:'Reset demo progress'},hi:{dashboard:'डैशबोर्ड',learn:'सीखें',analytics:'विश्लेषण',welcome:'अपनी आवाज़ में सीखें।',start:'सीखना शुरू करें',subjects:'आपके सीखने के विषय',language:'भाषा',lesson:'पाठ',quiz:'छोटी परीक्षा',submit:'उत्तर जाँचें',next:'अगला प्रश्न',speak:'उत्तर बोलें',correct:'सही उत्तर!',wrong:'सही नहीं। स्पष्टीकरण देखें।',recommend:'अनुकूली सुझाव',reset:'डेमो रीसेट करें'},kn:{dashboard:'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',learn:'ಕಲಿಯಿರಿ',analytics:'ವಿಶ್ಲೇಷಣೆ',welcome:'ನಿಮ್ಮ ಧ್ವನಿಯಲ್ಲಿ ಕಲಿಯಿರಿ.',start:'ಕಲಿಕೆ ಪ್ರಾರಂಭಿಸಿ',subjects:'ನಿಮ್ಮ ಕಲಿಕಾ ವಿಷಯಗಳು',language:'ಭಾಷೆ',lesson:'ಪಾಠ',quiz:'ತ್ವರಿತ ಪರೀಕ್ಷೆ',submit:'ಉತ್ತರ ಪರಿಶೀಲಿಸಿ',next:'ಮುಂದಿನ ಪ್ರಶ್ನೆ',speak:'ಉತ್ತರ ಹೇಳಿ',correct:'ಸರಿಯಾದ ಉತ್ತರ!',wrong:'ಸರಿಯಲ್ಲ. ವಿವರಣೆಯನ್ನು ನೋಡಿ.',recommend:'ವೈಯಕ್ತಿಕ ಸಲಹೆ',reset:'ಡೆಮೊ ಮರುಹೊಂದಿಸಿ'}};
const locales={en:'en-US',hi:'hi-IN',kn:'kn-IN'},opts=['A','B','C','D'];
function say(text,lang){if(!window.speechSynthesis)return;window.speechSynthesis.cancel();let u=new SpeechSynthesisUtterance(text);u.lang=locales[lang];window.speechSynthesis.speak(u)}
function Stat({label,value}){return <div className="stat"><span>{label}</span><strong>{value}</strong></div>}
export default function App(){const[lang,setLang]=useState('en'),t=words[lang],[page,setPage]=useState('dashboard'),[subjects,setSubjects]=useState([]),[subject,setSubject]=useState(null),[lessons,setLessons]=useState([]),[questions,setQuestions]=useState([]),[li,setLi]=useState(0),[qi,setQi]=useState(0),[choice,setChoice]=useState(''),[feedback,setFeedback]=useState(null),[analytics,setAnalytics]=useState(null),[history,setHistory]=useState([]),[rec,setRec]=useState(null),[error,setError]=useState(''),[busy,setBusy]=useState(false),[typed,setTyped]=useState('');
async function refresh(){try{let[s,a,h]=await Promise.all([api.subjects(),api.analytics(),api.history()]);setSubjects(s);setAnalytics(a);setHistory(h);if(!subject&&s.length)setSubject(s[0])}catch(e){setError(e.message+' — start the FastAPI backend on port 8000.')}}useEffect(()=>{refresh()},[]);
async function openSubject(s){setBusy(true);setError('');try{let[l,q,r]=await Promise.all([api.lessons(s.id),api.questions(s.id),api.recommend(s.id)]);setSubject(s);setLessons(l);setQuestions(q);setRec(r);setLi(0);setQi(0);setChoice('');setTyped('');setFeedback(null);setPage('learn')}catch(e){setError(e.message)}finally{setBusy(false)}}
let q=questions[qi],lesson=lessons[li],opt=q?{A:q.option_a,B:q.option_b,C:q.option_c,D:q.option_d}:{};
function listen() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!Recognition) {
    setError('Speech recognition is unavailable in this browser. Select an option or type A/B/C/D.');
    return;
  }

  const recognition = new Recognition();
  recognition.lang = locales[lang];
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.maxAlternatives = 3;

  setError('');
  setTyped('');

  recognition.onstart = () => {
    setError('Listening... Please speak your answer.');
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript.trim();
    setTyped(transcript);

    const match = transcript.toUpperCase().match(/^(?:OPTION\s+|ANSWER\s+|LETTER\s+)?([ABCD])\b/);
    if (match) {
      setChoice(match[1]);
      setError('Recognized answer: ' + match[1]);
    } else {
      setError('Heard "' + transcript + '". Please select or type option A, B, C, or D.');
    }
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);

    const messages = {
      network: 'Speech service connection failed. Check your internet connection and try again, or type A, B, C, or D below.',
      'not-allowed': 'Microphone access denied. Allow microphone access in Chrome settings.',
      'no-speech': 'No speech detected. Please try speaking again.',
      'audio-capture': 'Microphone not found. Check your microphone connection.'
    };

    if (event.error !== 'aborted') {
      setError(messages[event.error] || 'Speech recognition failed. You can type your answer instead.');
    }
  };

  try {
    recognition.start();
  } catch (error) {
    console.error('Could not start speech recognition:', error);
    setError('Could not start the microphone. Please try again.');
  }
}
async function submit(){let a=choice||((typed.trim().toUpperCase().match(/^(OPTION\s+)?([ABCD])\b/)||[])[2]);if(!q||!a){setError('Choose or say an option letter A, B, C or D.');return}setBusy(true);try{let f=await api.answer({subject_id:subject.id,question_id:q.id,selected_option:a});setFeedback(f);setRec(await api.recommend(subject.id));let[x,h]=await Promise.all([api.analytics(),api.history()]);setAnalytics(x);setHistory(h);setError('')}catch(e){setError(e.message)}finally{setBusy(false)}}
async function reset(){if(!confirm('Reset demo-student quiz history and learned Q-values?'))return;await api.reset();setFeedback(null);setQi(0);await refresh()}
return <div className="layout"><aside><div className="brand"><div className="logo"><AudioLines/></div><div><b>VoxLearn</b><small>ADAPTIVE ACADEMY</small></div></div><div className="student">Student workspace<br/><small>Demo learner</small></div>{[['dashboard',Activity],['learn',BookOpen],['analytics',BrainCircuit]].map(([p,I])=><button key={p} className={page===p?'nav active':'nav'} onClick={()=>setPage(p)}><I size={18}/>{t[p]}</button>)}<div className="sidebar-foot">✦ Q-learning enabled<br/><small>B.TECH PROJECT · v1.0</small></div></aside><main><header><span>VoxLearn　›　{t[page]}</span><label><Languages size={16}/><select value={lang} onChange={e=>setLang(e.target.value)}><option value="en">English</option><option value="hi">हिन्दी</option><option value="kn">ಕನ್ನಡ</option></select></label></header>{error&&<div className="error">{error}<button onClick={()=>setError('')}>×</button></div>}
{page==='dashboard'&&<div className="page"><section className="hero"><span>YOUR AI LEARNING COMPANION</span><h1>{t.welcome}</h1><p>Voice interaction, adaptive lessons and personal learning insights in one place.</p><button className="primary" onClick={()=>openSubject(subject||subjects[0])}>{t.start} <ChevronRight size={17}/></button><div className="hero-icon"><AudioLines size={56}/></div></section><div className="stats"><Stat label="Accuracy" value={`${analytics?.accuracy_percent||0}%`}/><Stat label="Attempts" value={analytics?.total_attempts||0}/><Stat label="Recent accuracy" value={`${analytics?.average_recent_accuracy||0}%`}/><Stat label="Active days" value={analytics?.engagement_sessions||0}/></div><h2>{t.subjects}</h2><div className="cards">{subjects.map((s,i)=><article key={s.id}><div className="subject-icon">{['Py','CS','∑'][i%3]}</div><h3>{s.name}</h3><p>{s.description}</p><button className="link" onClick={()=>openSubject(s)}>{t.start} <ChevronRight size={15}/></button></article>)}</div><div className="panel"><h3>{t.recommend}</h3><p>{rec?.rationale||'Complete a quiz to receive a personalized recommendation.'}</p>{rec&&<small>State: {rec.state} · Action: {rec.action}</small>}</div></div>}
{page==='learn'&&<div className="page"><div className="heading"><div><small>PERSONALIZED LEARNING SPACE</small><h2>{subject?.name||'Choose a subject'}</h2></div><button className="secondary" onClick={()=>setPage('dashboard')}>All subjects</button></div>{subject&&<div className="learning"><section className="panel"><small>{t.lesson} {li+1} / {lessons.length}</small><h3>{lesson?.title||'Lesson complete'}</h3><p className="lesson-text">{lesson?.content}</p><button className="secondary" onClick={()=>lesson&&say(lesson.title+'. '+lesson.content,lang)}><Volume2 size={16}/> Read lesson aloud</button><div className="row"><button className="secondary" disabled={li===0} onClick={()=>setLi(Math.max(0,li-1))}>Previous</button><button className="secondary" disabled={li>=lessons.length-1} onClick={()=>setLi(Math.min(lessons.length-1,li+1))}>Next lesson</button></div></section><section className="panel"><small>{t.quiz.toUpperCase()} · {Math.min(qi+1,questions.length)}/{questions.length}</small><h3>{t.voice||'Voice tutor'}</h3>{q?<><h4>{q.prompt}</h4><div className="answers">{opts&&opts.A&&opts&&Object.entries(opt).map(([k,v])=><button disabled={!!feedback} className={choice===k?'chosen':''} key={k} onClick={()=>{setChoice(k);setTyped('')}}><b>{k}</b>{v}</button>)}</div><div className="row"><button className="secondary" disabled={!!feedback} onClick={listen}><Mic size={16}/>{t.speak}</button><input value={typed} disabled={!!feedback} onChange={e=>setTyped(e.target.value)} placeholder="Type option A/B/C/D"/></div>{feedback&&<div className={feedback.is_correct?'feedback good':'feedback bad'}><b>{feedback.is_correct?t.correct:t.wrong}</b><p>{feedback.explanation}</p><small>Reward {feedback.reward>0?'+':''}{feedback.reward} · Next action: {feedback.recommended_action}</small><button className="secondary" onClick={()=>say(feedback.explanation,lang)}><Volume2 size={15}/> Speak feedback</button></div>}{!feedback?<button className="primary wide" disabled={busy} onClick={submit}>{t.submit}</button>:<button className="primary wide" onClick={()=>{setFeedback(null);setChoice('');setTyped('');setQi(v=>v+1)}}>{t.next}</button>}</>:<div><CheckCircle2/><p>Questions complete for this subject.</p><button className="secondary" onClick={()=>{setQi(0);setFeedback(null)}}><RotateCcw size={15}/> Practice again</button></div>}</section></div>}</div>}
{page==='analytics'&&<div className="page"><div className="heading"><div><small>YOUR LEARNING DATA</small><h2>{t.analytics}</h2></div><button className="secondary" onClick={reset}><RotateCcw size={15}/>{t.reset}</button></div><div className="stats"><Stat label="Accuracy" value={`${analytics?.accuracy_percent||0}%`}/><Stat label="Attempts" value={analytics?.total_attempts||0}/><Stat label="Recent accuracy" value={`${analytics?.average_recent_accuracy||0}%`}/><Stat label="Active days" value={analytics?.engagement_sessions||0}/></div><div className="panel chart"><h3>Accuracy by subject</h3><ResponsiveContainer width="100%" height={250}><BarChart data={analytics?.subjects||[]}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="subject"/><YAxis domain={[0,100]}/><Tooltip/><Bar dataKey="accuracy_percent" fill="#6758e8" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></div><div className="panel"><h3>Recent activity</h3>{history.length?history.map(x=><div className="history" key={x.id}><span>{x.is_correct?'✓':'×'}</span><div><b>{x.question}</b><small>{x.subject} · Selected {x.selected_option}</small></div><strong>{x.is_correct?'Correct':'Incorrect'}</strong></div>):<p>No activity yet. Start a lesson and submit an answer.</p>}<p className="note">Evaluation note: compare pre-test and post-test scores under comparable conditions. Accuracy trends alone do not prove that RL caused learning improvement.</p></div></div>}
<footer>VoxLearn · B.Tech AI/ML prototype <span>● API-powered</span></footer></main></div>}
