from sqlalchemy.orm import Session
from .models import Subject, Lesson, Question
DATA = [
("Python Fundamentals","Variables, conditions and loops",[
("Variables and Types",1,"A variable stores a value. Common Python types include int, float, str and bool."),
("Conditions",2,"An if statement runs code when a condition is true. elif checks another condition; else is the fallback."),
("Loops",3,"A for loop iterates over a sequence. A while loop repeats while its condition remains true.")],[
(0,"Which symbol assigns a value in Python?","==","=","!=","->","B","A single equals sign assigns; == compares."),
(0,"Which type represents whole numbers?","str","float","int","bool","C","int represents integers."),
(1,"Which keyword checks an alternative condition?","elif","repeat","caseof","next","A","elif checks another condition."),
(1,"When does else run?","Always first","When prior conditions are false","Declares a variable","Ends the program","B","else is the fallback branch."),
(2,"Which loop commonly iterates over a list?","if","for","def","class","B","for iterates over an iterable."),
(2,"A while loop continues while its condition is…","false","missing","true","a string","C","It repeats while the condition is true.")]),
("Computer Science Basics","Algorithms, data structures and databases",[
("Algorithms",1,"An algorithm is a finite sequence of clear steps for solving a problem."),
("Data Structures",2,"Stacks, queues, lists, trees and hash tables organize data in different ways."),
("Database Basics",3,"A relational database stores data in tables. A primary key uniquely identifies a row.")],[
(0,"What is an algorithm?","A brand","A finite sequence of steps","A cable","A language","B","An algorithm describes steps to solve a problem."),
(0,"Which structure follows LIFO?","Queue","Stack","Tree","Graph","B","A stack follows last-in, first-out."),
(1,"Which structure follows FIFO?","Stack","Queue","Heap","Tree","B","A queue follows first-in, first-out."),
(1,"Which structure maps keys to values?","Hash table","Stack","Queue","Array only","A","Hash tables associate keys with values."),
(2,"What uniquely identifies a row?","Foreign text","Primary key","Color","Label only","B","A primary key uniquely identifies a record."),
(2,"A foreign key is used to…","Relate tables","Compress audio","Render graphics","Compile code","A","A foreign key references another table's key.")]),
("Mathematics for Computing","Binary, logic and computational complexity",[
("Binary Numbers",1,"Binary uses digits 0 and 1. Each position represents a power of two."),
("Boolean Logic",2,"AND is true when both inputs are true. OR is true when at least one input is true."),
("Big-O Basics",3,"Big-O describes how algorithm resource requirements grow as input size grows.")],[
(0,"Which digits are used in binary?","0 and 1","0 to 7","0 to 9","1 and 2","A","Binary uses only 0 and 1."),
(0,"Binary 10 equals which decimal value?","1","2","3","10","B","Binary 10 equals 1×2 + 0 = 2."),
(1,"AND is true when…","Either input true","Both inputs true","Both false","Inputs differ","B","AND requires both inputs true."),
(1,"OR is false when…","Both inputs false","Both true","One true","Inputs differ","A","OR is false only when both inputs are false."),
(2,"Big-O describes…","Screen size","Growth of resource use","Variable names","Audio volume","B","Big-O characterizes asymptotic growth."),
(2,"Which grows slower for large n?","O(n²)","O(n)","O(2ⁿ)","O(n!)","B","Linear growth is slower than these alternatives.")])]
def seed_database(db: Session):
    if db.query(Subject).count(): return
    for name, desc, lessons, questions in DATA:
        s=Subject(name=name, description=desc); db.add(s); db.flush()
        ids=[]
        for title,difficulty,content in lessons:
            l=Lesson(subject_id=s.id,title=title,difficulty=difficulty,content=content); db.add(l); db.flush(); ids.append(l.id)
        for idx,prompt,a,b,c,d,correct,explanation in questions:
            db.add(Question(subject_id=s.id,lesson_id=ids[idx],prompt=prompt,option_a=a,option_b=b,option_c=c,option_d=d,correct_option=correct,explanation=explanation))
    db.commit()
