import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

# אתחול ה-LocalStorage
local_storage = LocalStorage()

st.title("🎓 GradeMaster Pro - ניהול ציונים חכם")

# --- פונקציית טעינה משופרת ---
# אנחנו בודקים אם יש נתונים שמורים בזיכרון המכשיר
saved_data = local_storage.getItem("user_grades")

# אתחול רשימת הקורסים בזיכרון האפליקציה (Session State)
if 'subjects' not in st.session_state:
    if saved_data is not None and isinstance(saved_data, list):
        st.session_state.subjects = saved_data
    else:
        st.session_state.subjects = []

# --- תפריט צד ---
with st.sidebar:
    st.header("➕ הוספת קורס")
    name = st.text_input("שם הקורס")
    grade = st.number_input("ציון", 0, 100, 85)
    weight = st.number_input("נקודות זכות (נ\"ז)", 1.0, 10.0, 2.0, 0.5)
    year = st.selectbox("שנה:", ["שנה א'", "שנה ב'", "שנה ג'", "שנה ד'"])
    
    if st.button("שמור במכשיר 💾"):
        if name:
            new_subject = {
                "קורס": name,
                "שנה": year,
                "ציון": float(grade),
                "נ\"ז": float(weight)
            }
            # עדכון הרשימה בזיכרון הנוכחי
            st.session_state.subjects.append(new_subject)
            # שמירה פיזית בזיכרון הקבוע של המכשיר
            local_storage.setItem("user_grades", st.session_state.subjects)
            st.success(f"הקורס {name} נשמר!")
            st.rerun()
        else:
            st.error("נא להזין שם קורס")

    st.divider()
    if st.button("🗑️ מחק הכל מהמכשיר"):
        local_storage.deleteAll()
        st.session_state.subjects = []
        st.rerun()

# --- הצגת הנתונים ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישובים
    total_w = round(df['נ\"ז'].sum(), 1)
    weighted_avg = round((df['ציון'] * df['נ\"ז']).sum() / total_w, 2)
    
    col1, col2 = st.columns(2)
    col1.metric("🎓 ממוצע כולל", f"{weighted_avg:.2f}")
    col2.metric("📜 סך נ\"ז", f"{total_w}")

    st.divider()
    st.subheader("📋 רשימת הקורסים השמורה שלך")
    
    # הצגה נקייה בטבלה
    display_df = df.copy()
    display_df['ציון'] = display_df['ציון'].map(lambda x: f"{x:.2f}")
    st.dataframe(display_df[["קורס", "שנה", "ציון", "נ\"ז"]], use_container_width=True)

    # גרף
    st.subheader("📊 ממוצעים לפי שנה")
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['נ\"ז']).sum() / x['נ\"ז'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']
    fig = px.bar(year_stats, x='שנה', y='ממוצע שנתי', color='שנה', text_auto='.2f')
    st.plotly_chart(fig, use_container_width=True)

    # סימולטור ניבוי
    st.divider()
    st.subheader("🎯 ניבוי ציון לממוצע יעד")
    c1, c2 = st.columns(2)
    target = c1.number_input("ממוצע יעד:", 60.0, 100.0, 90.0)
    future_w = c2.number_input("נ\"ז שנותרו:", 1.0, 100.0, 10.0)
    needed = (target * (total_w + future_w) - (df['ציון'] * df['נ\"ז']).sum()) / future_w
    st.info(f"כדי להגיע ל-{target:.2f}, עליך להוציא ממוצע של **{needed:.2f}** בקורסים שנותרו.")

else:
    st.info("אין נתונים שמורים. הוסף קורס ושמור אותו כדי שיופיע כאן גם אחרי רענון.")
