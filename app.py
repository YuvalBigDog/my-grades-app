import streamlit as st
import pandas as pd
import plotly.express as px
import json

# הגדרות דף
st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

# פונקציות עזר לשימוש ב-Session State (הזיכרון המקומי יסונכרן לכאן)
if 'subjects' not in st.session_state:
    st.session_state.subjects = []

st.title("🎓 GradeMaster Pro - ניהול ציונים אישי")
st.write("הנתונים נשמרים באופן מקומי על המכשיר שלך בלבד.")

# --- תפריט צד ---
with st.sidebar:
    st.header("➕ הוספת קורס")
    name = st.text_input("שם הקורס")
    grade = st.number_input("ציון", 0, 100, 85)
    weight = st.number_input("נקודות זכות (נ\"ז)", 1.0, 10.0, 2.0, 0.5)
    year = st.selectbox("שנה:", ["שנה א'", "שנה ב'", "שנה ג'", "שנה ד'"])
    
    if st.button("הוסף ושמור במכשיר"):
        if name:
            new_subject = {
                "קורס": name,
                "שנה": year,
                "ציון": float(grade),
                "נ\"ז": float(weight)
            }
            st.session_state.subjects.append(new_subject)
            st.success(f"הקורס {name} נוסף!")
            st.rerun()
        else:
            st.error("נא להזין שם קורס")

    st.divider()
    if st.button("🗑️ מחק הכל"):
        st.session_state.subjects = []
        st.rerun()

# --- תצוגת נתונים ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישובים
    total_w = round(df['נ\"ז'].sum(), 1)
    weighted_avg = round((df['ציון'] * df['נ\"ז']).sum() / total_w, 2)
    
    col1, col2 = st.columns(2)
    col1.metric("🎓 ממוצע כולל", f"{weighted_avg:.2f}")
    col2.metric("📜 סך נ\"ז", f"{total_w}")

    st.divider()

    st.subheader("📋 רשימת הקורסים שלי")
    # הצגת הטבלה עם עיגול
    display_df = df.copy()
    display_df['ציון'] = display_df['ציון'].map(lambda x: f"{x:.2f}")
    st.dataframe(display_df[["קורס", "שנה", "ציון", "נ\"ז"]], use_container_width=True)

    st.divider()

    # השוואת שנים
    st.subheader("📊 ממוצעים לפי שנה")
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['נ\"ז']).sum() / x['נ\"ז'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']
    
    fig = px.bar(year_stats, x='שנה', y='ממוצע שנתי', color='שנה', text_auto='.2f')
    fig.update_layout(yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)

    # סימולטור ניבוי
    st.divider()
    st.subheader("🎯 ניבוי: מה הציון הבא?")
    c1, c2 = st.columns(2)
    target_avg = c1.number_input("ממוצע יעד:", 60.0, 100.0, 90.0)
    future_w = c2.number_input("נ\"ז של המבחנים הקרובים:", 1.0, 100.0, 10.0)
    
    current_pts = (df['ציון'] * df['נ\"ז']).sum()
    needed = (target_avg * (total_w + future_w) - current_pts) / future_w
    
    if needed > 100:
        st.warning(f"תצטרך ממוצע של {needed:.2f}. קצת קשוח, לא? 😉")
    elif needed < 0:
        st.success(f"אתה כבר מעל היעד של {target_avg}!")
    else:
        st.info(f"כדי להגיע ל-{target_avg:.2f}, עליך להוציא ממוצע של **{needed:.2f}** במבחנים הקרובים.")

else:
    st.info("הכנס קורס בתפריט הצד כדי להתחיל. הנתונים יישמרו בדפדפן שלך.")
