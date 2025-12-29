import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

st.title("🎓 GradeMaster Pro - ניהול וניבוי ציונים")

# אתחול נתונים
if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# --- הזנת נתונים בתפריט הצד ---
with st.sidebar:
    st.header("➕ הוספת קורס")
    name = st.text_input("שם הקורס")
    grade = st.number_input("ציון", 0, 100, 85)
    weight = st.number_input("נקודות זכות (נ\"ז)", 1.0, 10.0, 2.0, 0.5)
    year = st.selectbox("שנה:", ["שנה א'", "שנה ב'", "שנה ג'", "שנה ד'"])
    
    if st.button("הוסף לרשימה"):
        if name:
            st.session_state.subjects.append({
                "קורס": name,
                "שנה": year,
                "ציון": float(grade),
                "נ\"ז": float(weight)
            })
            st.success(f"הוספת את {name}")
        else:
            st.error("חובה להזין שם קורס!")

    st.divider()
    if st.button("🗑️ מחק הכל"):
        st.session_state.subjects = []
        st.rerun()

# --- הצגת הנתונים ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישובים מעוגלים מראש
    total_w = round(df['נ\"ז'].sum(), 1)
    weighted_avg = round((df['ציון'] * df['נ\"ז']).sum() / total_w, 2)
    
    # מדדים עליונים
    col1, col2 = st.columns(2)
    col1.metric("🎓 ממוצע כולל", f"{weighted_avg:.2f}")
    col2.metric("📜 סך נ\"ז שנצברו", f"{total_w}")

    st.divider()

    # 1. טבלת הקורסים - כאן התיקון הקריטי
    st.subheader("📋 רשימת הקורסים המלאה")
    # יצירת עותק נקי לתצוגה בלבד עם עיגול מחמיר
    display_df = df.copy()
    display_df['ציון'] = display_df['ציון'].apply(lambda x: f"{x:.2f}")
    display_df['נ\"ז'] = display_df['נ\"ז'].apply(lambda x: f"{x:.1f}")
    
    # הצגת הטבלה כשהקורס הוא העמודה הראשונה
    st.dataframe(display_df[["קורס", "שנה", "ציון", "נ\"ז"]], use_container_width=True)

    st.divider()

    # 2. השוואת שנים
    st.subheader("📊 ממוצעים לפי שנה")
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['נ\"ז']).sum() / x['נ\"ז'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']
    year_stats['ממוצע שנתי'] = year_stats['ממוצע שנתי'].apply(lambda x: round(x, 2))
    
    # טבלת סיכום שנה (סטטית וברורה)
    st.table(year_stats)

    # גרף
    fig = px.bar(year_stats, x='שנה', y='ממוצע שנתי', color='שנה', text_auto='.2f')
    fig.update_layout(yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)

    # 3. מחשבון ניבוי (המבוקש)
    st.divider()
    st.subheader("🎯 ניבוי: מה הציון שצריך לקבל?")
    
    c1, c2 = st.columns(2)
    with c1:
        target_avg = st.number_input("מה ממוצע היעד שלך?", 60.0, 100.0, 90.0, 0.5)
    with c2:
        future_w = st.number_input("נ\"ז של המבחנים הקרובים (או אלו שנותרו לתואר):", 1.0, 150.0, 10.0, 0.5)
    
    current_points = (df['ציון'] * df['נ\"ז']).sum()
    required_grade = (target_avg * (total_w + future_w) - current_points) / future_w
    
    if required_grade > 100:
        st.warning(f"כדי להגיע ל-{target_avg:.2f}, תצטרך ממוצע בלתי אפשרי של {required_grade:.2f} 😰")
    elif required_grade < 0:
        st.success(f"אתה כבר מעל היעד! הממוצע יהיה מעל {target_avg:.2f} בכל מקרה.")
    else:
        st.info(f"כדי להגיע לממוצע {target_avg:.2f}, עליך להוציא ממוצע של **{required_grade:.2f}** בקורסים שנותרו.")

else:
    st.info("GradeMaster Pro מחכה שתזין קורס בתפריט הצד!")
