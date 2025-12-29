import streamlit as st
import pandas as pd
import plotly.express as px

# גרסה 3.0 - כולל שיוך לשנים והשוואה
st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

st.title("🎓 GradeMaster Pro - ניהול והשוואת שנים")

if 'subjects' not in st.session_state:
    st.session_state.subjects = []

with st.sidebar:
    st.header("הוספת מקצוע")
    name = st.text_input("שם המקצוע")
    grade = st.number_input("ציון", min_value=0, max_value=100, value=85)
    weight = st.number_input("נקודות זכות (נ\"ז)", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
    
    # הנה השיוך לשנה שחיפשנו:
    year = st.selectbox("בחר שנה:", ["שנה א'", "שנה ב'", "שנה ג'", "שנה ד'"])
    
    if st.button("הוסף למערכת"):
        if name:
            st.session_state.subjects.append({"שנה": year, "מקצוע": name, "ציון": grade, "משקל": weight})
            st.success(f"הוספת את {name} ל{year}")
        else:
            st.error("נא להזין שם מקצוע")

    if st.button("נקה הכל"):
        st.session_state.subjects = []
        st.rerun()

if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישוב ממוצעים להשוואה בין שנים
    year_summary = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['משקל']).sum() / x['משקל'].sum()
    ).reset_index()
    year_summary.columns = ['שנה', 'ממוצע שנתי']

    col1, col2 = st.columns(2)
    with col1:
        total_avg = (df['ציון'] * df['משקל']).sum() / df['משקל'].sum()
        st.metric("ממוצע תואר כולל", f"{total_avg:.2f}")
    with col2:
        st.subheader("📋 פירוט לפי שנים")
        st.table(year_summary)

    st.divider()

    # גרף השוואת שנים - כאן תראה את ההתקדמות/ירידה
    st.subheader("📊 השוואת ממוצעים בין השנים")
    fig_compare = px.bar(year_summary, x='שנה', y='ממוצע שנתי', 
                         color='שנה', text_auto='.1f',
                         title="איך הממוצע שלך משתנה בין השנים?")
    fig_compare.update_layout(yaxis_range=[0, 105])
    st.plotly_chart(fig_compare, use_container_width=True)

else:
    st.info("השתמש בתפריט הצדדי כדי להוסיף מקצועות ולשייך אותם לשנים.")
