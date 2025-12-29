import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓")

st.title("🎓 GradeMaster Pro - ניהול ציונים חכם")

if 'subjects' not in st.session_state:
    st.session_state.subjects = []

with st.sidebar:
    st.header("הוספת מקצוע חדש")
    name = st.text_input("שם המקצוע")
    grade = st.number_input("ציון", min_value=0, max_value=100, value=90)
    weight = st.number_input("נקודות זכות (נ\"ז)", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
    # הוספת בחירת שנה
    year = st.selectbox("שנה סטודנטיאלית", ["א'", "ב'", "ג'", "ד'"])
    
    if st.button("הוסף למערכת"):
        if name:
            st.session_state.subjects.append({"שנה": year, "מקצוע": name, "ציון": grade, "משקל": weight})
            st.success(f"הוספת את {name} לשנה {year}!")
        else:
            st.error("נא להזין שם מקצוע")

    if st.button("נקה הכל"):
        st.session_state.subjects = []
        st.rerun()

if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # הצגת ממוצעים לפי שנה
    st.subheader("📊 סיכום לפי שנים")
    for y in df['שנה'].unique():
        year_df = df[df['שנה'] == y]
        y_avg = (year_df['ציון'] * year_df['משקל']).sum() / year_df['משקל'].sum()
        st.write(f"**ממוצע שנה {y}:** {y_avg:.2f}")

    st.divider()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("פירוט ציונים")
        st.dataframe(df, use_container_width=True)
        
    with col2:
        total_weight = df['משקל'].sum()
        weighted_avg = (df['ציון'] * df['משקל']).sum() / total_weight
        st.metric("ממוצע כולל", f"{weighted_avg:.2f}")

    st.subheader("📈 גרף התקדמות")
    fig = px.scatter(df, x="מקצוע", y="ציון", size="משקל", color="שנה", hover_name="מקצוע", size_max=40)
    st.plotly_chart(fig)

    # סימולטור יעד
    st.divider()
    st.subheader("🎯 סימולטור יעד")
    target_avg = st.slider("מה ממוצע היעד הכולל?", min_value=int(weighted_avg) if weighted_avg < 100 else 90, max_value=100, value=95)
    remaining_weight = st.number_input("כמה נ\"ז נשארו לתואר?", min_value=1.0, value=10.0)
    
    current_sum = (df['ציון'] * df['משקל']).sum()
    total_new_weight = total_weight + remaining_weight
    required_score = (target_avg * total_new_weight - current_sum) / remaining_weight
    
    if required_score > 100:
        st.warning(f"כדי להגיע ל-{target_avg}, תצטרך ממוצע {required_score:.1f}. זה קצת גבוה, אולי נוריד יעד? 😉")
    elif required_score < 0:
        st.success("אתה כבר מעל היעד! כל ציון שתקבל יהיה בונוס.")
    else:
        st.info(f"עליך להוציא ממוצע של **{required_score:.1f}** בשאר התואר כדי להגיע ל-{target_avg}.")
else:
    st.info("המערכת מחכה לציונים הראשונים שלך...")
