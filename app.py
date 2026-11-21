import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from courses import COURSES



from database import (
    initialize_database,
    add_student,
    get_all_mastery,
    get_mastery,
    save_attempt,
    get_student_stats
)
from questions import QUESTIONS
from learner_model import update_learner_model, get_mastery_status, get_difficulty
from concept_graph import create_concept_graph

st.set_page_config(page_title="Adaptive Exam Tutor",page_icon="🎓",layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0B1120;
    color: #F1F5F9;
}
[data-testid="stSidebar"] {
    background-color: #111B2E;
    border-right: 1px solid #26344A;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #F1F5F9 !important;
}
p, label, span {
    color: #D1D9E6;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #17243A, #1B2C45);
    padding: 18px;
    border: 1px solid #2B3C56;
    border-radius: 16px;
}
.stButton > button {
    background-color: #6366F1;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #818CF8;
    color: white;
}
div[data-testid="stProgressBar"] > div > div {
    background-color: #818CF8;
}
hr {
    border-color: #26344A;
}
</style>
""", unsafe_allow_html=True)

initialize_database()

CONCEPTS = [
    "Electric Current",
    "Voltage",
    "Resistance",
    "Ohm's Law",
    "Series Circuits",
    "Parallel Circuits",
    "Electric Power"
]

st.title("🎓 Adaptive Exam-Prep Tutor")
st.caption("Personalized learning powered by an adaptive learner model")

if "student" not in st.session_state:
    st.session_state.student = ""

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = QUESTIONS

with st.sidebar:
    st.markdown("## 🎓 Adaptive Tutor")
    st.caption("Personalized Learning Platform")

    st.divider()

    st.subheader("👤 Student Profile")

    student_name = st.text_input("Student Name", value=st.session_state.student)

    if st.button("Set Student", use_container_width=True):
        if student_name.strip():
            st.session_state.student = student_name.strip()
            add_student(student_name.strip())
            st.success("Profile updated")

    st.divider()

    

    selected_course = st.selectbox(
        "Choose Course",
        list(COURSES.keys())
    )

    course_info = COURSES[selected_course]
    st.caption(course_info["description"])

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Home",
            "Diagnostic Test",
            "My Learning",
            "Concept Graph",
            "Teacher Dashboard"
        ]
    )

    st.divider()
    st.caption("Learning • Practice • Mastery")

course_info = COURSES[selected_course]

st.caption(course_info["description"])

page = st.radio(
    "Navigation",
    ["Home","Diagnostic Test","My Learning","Concept Graph","Teacher Dashboard"]
)

if not st.session_state.student:
    st.info("Enter your name in the sidebar and click Set Student to begin.")
    st.stop()

student = st.session_state.student


cols = st.columns(2)

for i, (course_name, course) in enumerate(COURSES.items()):
    with cols[i % 2]:
        st.markdown(
            f"""
            <div style="
                background:linear-gradient(135deg,#17243A,#243B60);
                padding:22px;
                border-radius:18px;
                border:1px solid #34466A;
                min-height:180px;">
                <h3>{course['icon']} {course_name}</h3>
                <p>{course['description']}</p>
                <p>📖 Chapter: {course['chapter']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(f"Open {course_name}", key=f"open_{course_name}", use_container_width=True):
            st.session_state.open_course = course_name
            st.rerun()

if "open_course" in st.session_state:
    opened_course = st.session_state.open_course
    info = COURSES[opened_course]

    st.divider()
    st.subheader(f"{info['icon']} {opened_course}")
    st.write(info["description"])
    st.write(f"**Chapter:** {info['chapter']}")
    st.write("### Concepts in this course")

    for concept in info["concepts"]:
        st.markdown(f"- 📘 {concept}")

    if st.button("Close Course", key="close_course"):
        del st.session_state.open_course
        st.rerun()

    mastery = get_all_mastery(student)
    average = sum(mastery.values()) / len(mastery) if mastery else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Concepts Tracked", len(course_info["concepts"]))
    c2.metric("Overall Mastery", f"{average:.1f}%")
    c3.metric("Learning Status", get_mastery_status(average))

    st.markdown("### 🚀 Your Learning Journey")
    a, b, c = st.columns(3)

    a.info("**1. Assess**\n\nTake a diagnostic test.")
    b.info("**2. Adapt**\n\nPractice weak concepts.")
    c.info("**3. Improve**\n\nMaster every concept.")

elif page == "Diagnostic Test":
    st.subheader("📝 Diagnostic Test")
    st.write("Answer questions to check your understanding of Electricity.")

    if not st.session_state.quiz_active:
        if st.button("Start Test"):
            st.session_state.quiz_active = True
            st.session_state.quiz_index = 0
            st.session_state.quiz_answers = {}
            st.rerun()

    if st.session_state.quiz_active:
        index = st.session_state.quiz_index

        if index < len(st.session_state.quiz_questions):
            q = st.session_state.quiz_questions[index]

            st.progress((index+1)/len(st.session_state.quiz_questions))
            st.write(f"Question {index+1} of {len(st.session_state.quiz_questions)}")
            st.write(f"Concept: {q['concept']} | Difficulty: {q['difficulty']}")
            st.markdown(f"### {q['question']}")

            selected = st.radio(
                "Choose your answer",
                q["options"],
                key=f"answer_{index}"
            )

            if st.button("Submit Answer",key=f"submit_{index}"):
                is_correct = selected == q["answer"]

                save_attempt(
                    student,
                    q["concept"],
                    q["question"],
                    selected,
                    q["answer"],
                    is_correct
                )

                score = update_learner_model(student,q["concept"],is_correct)

                st.session_state.quiz_answers[index] = is_correct

                if is_correct:
                    st.success(f"Correct! Mastery: {score:.1f}%")
                else:
                    st.error(f"Incorrect. Correct answer: {q['answer']}")
                    st.info(q["explanation"])

                st.session_state.quiz_index += 1
                st.rerun()

        else:
            correct_count = sum(st.session_state.quiz_answers.values())
            total = len(st.session_state.quiz_questions)

            st.success("Diagnostic test completed!")
            st.metric("Your Score",f"{correct_count}/{total}")
            st.metric("Percentage",f"{correct_count/total*100:.1f}%")

            if st.button("Finish Test"):
                st.session_state.quiz_active = False
                st.session_state.quiz_index = 0
                st.session_state.quiz_answers = {}
                st.rerun()

elif page == "My Learning":
    st.subheader("📊 My Learning Progress")
    mastery = get_all_mastery(student)

    if not mastery:
        st.info("Take the diagnostic test to generate your mastery scores.")
    else:
        for concept in CONCEPTS:
            score = mastery.get(concept,0)
            st.write(f"**{concept}** — {get_mastery_status(score)}")
            st.progress(int(score))
            st.caption(f"Mastery: {score:.1f}% | Recommended difficulty: {get_difficulty(score)}")

        fig = go.Figure(go.Bar(
            x=list(mastery.keys()),
            y=list(mastery.values())
        ))
        fig.update_layout(
            title="Concept Mastery",
            yaxis_title="Mastery (%)",
            yaxis_range=[0,100]
        )
        st.plotly_chart(fig,use_container_width=True)

elif page == "Concept Graph":
    st.subheader("🧠 Electricity Concept Graph")
    graph = create_concept_graph()
    mastery = get_all_mastery(student)

    pos = nx.spring_layout(graph,seed=42)
    edges = list(graph.edges())

    edge_x = []
    edge_y = []

    for source,target in edges:
        x0,y0 = pos[source]
        x1,y1 = pos[target]
        edge_x.extend([x0,x1,None])
        edge_y.extend([y0,y1,None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1,color="gray"),
        hoverinfo="none"
    )

    node_x = []
    node_y = []
    node_text = []

    for node in graph.nodes():
        x,y = pos[node]
        node_x.append(x)
        node_y.append(y)
        score = mastery.get(node,0)
        node_text.append(f"{node}<br>Mastery: {score:.1f}%")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=list(graph.nodes()),
        textposition="bottom center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(size=25)
    )

    fig = go.Figure([edge_trace,node_trace])
    fig.update_layout(
        title="Concept Prerequisites",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    st.plotly_chart(fig,use_container_width=True)
    st.write("Arrows show which concepts help you understand the next concept.")

elif page == "Teacher Dashboard":
    st.subheader("👨‍🏫 Teacher Dashboard")

    students,average,concept_stats,student_stats = get_student_stats()

    c1,c2 = st.columns(2)
    c1.metric("Total Students",students)
    c2.metric("Average Class Mastery",f"{average:.1f}%")

    if concept_stats:
        st.write("### Concepts Needing Attention")
        concepts = [row[0] for row in concept_stats]
        scores = [row[1] for row in concept_stats]

        fig = go.Figure(go.Bar(x=concepts,y=scores))
        fig.update_layout(
            yaxis_title="Average Mastery (%)",
            yaxis_range=[0,100]
        )
        st.plotly_chart(fig,use_container_width=True)

        st.write("### Weak Concepts")
        for concept,score in concept_stats:
            if score < 40:
                st.warning(f"{concept}: {score:.1f}% mastery")

    if student_stats:
        st.write("### Student Progress")
        for name,score in student_stats:
            st.write(f"**{name}** — {score:.1f}% average mastery")

            from courses import COURSES



