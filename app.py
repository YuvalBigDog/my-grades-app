import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

st.title("🎓 GradeMaster Pro - ניהול וניבוי ציונים")

if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# --- הזנת נתונים בתפריט הצד ---
with st.sidebar:
    st.header("➕ הוספת קורס")
    name = st.text_input("שם הקורס (חובה לראות בטבלה)")
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

# --- הצגת הנתונים במסך הראשי ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישובים מעוגלים ל-2 ספרות
    total_w = round(df['נ\"ז'].sum(), 1)
    weighted_avg = round((df['ציון'] * df['נ\"ז']).sum() / total_w, 2)
    
    col1, col2 = st.columns(2)
    col1.metric("🎓 ממוצע כולל (סופי)", f"{weighted_avg:.2f}")
    col2.metric("📜 סך נ\"ז", f"{total_w}")

    st.divider()

    # 1. טבלת הקורסים (עם שמות הקורסים כפי שביקשת)
    st.subheader("📋 רשימת הקורסים שלי")
    # הצגת הטבלה עם עיגול מספרים
    st.dataframe(df[["קורס", "שנה", "ציון", "נ\"ז"]], use_container_width=True)

    st.divider()

    # 2. השוואת שנים בגרף נקי (2 ספרות)
    st.subheader("📊 השוואה בין שנים")
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['נ\"ז']).sum() / x['נ\"ז'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']
    year_stats['ממוצע שנתי'] = year_stats['ממוצע שנתי'].round(2)
    
    fig = px.bar(year_stats, x='שנה', y='ממוצע שנתי', color='שנה', text_auto='.2f')
    fig.update_layout(yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)

    # 3. מחשבון ניבוי (Prediction) - הפיצ'ר שחייב לעבוד
    st.divider()
    st.subheader("🎯 ניבוי: איזה ציון אני צריך במבחנים הבאים?")
    
    c1, c2 = st.columns(2)
    with c1:
        target_avg = st.number_input("מה ממוצע היעד שלך?", 60.0, 100.0, 90.0, 0.5)
    with c2:
        future_w = st.number_input("כמה נ\"ז נשארו (מבחנים קרובים)?", 1.0, 100.0, 10.0, 0.5)
    
    # נוסחת הניבוי
    current_points = (df['ציון'] * df['נ\"ז']).sum()
    required_grade = (target_avg * (total_w + future_w) - current_points) / future_w
    
    if required_grade > 100:
        st.warning(f"כדי להגיע ל-{target_avg}, תצטרך ממוצע של {required_grade:.2f}. זה מעל 100, אז כדאי להנמיך ציפיות 😅")
    elif required_grade < 0:
        st.success(f"אתה כבר שם! גם אם תקבל 0 במבחנים הקרובים, הממוצע יהיה מעל {target_avg}")
    else:
        st.info(f"כדי להגיע לממוצע {target_avg}, אתה צריך להוציא ממוצע של **{required_grade:.2f}** במבחנים הקרובים.")

else:
    st.info("הכנס קורס בתפריט הצדדי כדי להתחיל לראות נתונים.")
