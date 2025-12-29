import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

st.title("🎓 GradeMaster Pro - ניהול ציונים מתקדם")

if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# --- תפריט צד ---
with st.sidebar:
    st.header("הוספת קורס חדש")
    name = st.text_input("שם הקורס")
    grade = st.number_input("ציון", min_value=0, max_value=100, value=85)
    weight = st.number_input("נקודות זכות (נ\"ז)", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
    year = st.selectbox("שייך לשנה:", ["שנה א'", "שנה ב'", "שנה ג'", "שנה ד'"])
    
    if st.button("הוסף למערכת"):
        if name:
            st.session_state.subjects.append({"שנה": year, "קורס": name, "ציון": grade, "משקל": weight})
            st.success(f"הוספת את {name} בהצלחה!")
        else:
            st.error("נא להזין שם קורס")

    if st.button("איפוס נתונים"):
        st.session_state.subjects = []
        st.rerun()

# --- תצוגת נתונים ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישובים
    total_w = df['משקל'].sum()
    total_avg = (df['ציון'] * df['משקל']).sum() / total_w
    
    # הצגת מדדים בולטים
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("ממוצע תואר כולל", f"{total_avg:.2f}")
    col_m2.metric("סך נ\"ז שנצברו", f"{total_w:.1f}")

    st.divider()

    # טבלת פירוט הקורסים (מה שביקשת להחזיר)
    st.subheader("📋 רשימת הקורסים שלי")
    # עיגול מספרים לתצוגה יפה
    df_display = df.copy()
    st.dataframe(df_display, use_container_width=True)

    st.divider()

    # גרף השוואת שנים
    st.subheader("📊 השוואת ממוצעים בין השנים")
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['משקל']).sum() / x['משקל'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']
    
    fig = px.bar(year_stats, x='שנה', y='ממוצע שנתי', color='שנה', 
                 text_auto='.2f', title="התקדמות אקדמית לפי שנה")
    fig.update_layout(yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)

    # --- סימולטור יעד (חזר למרכז הבמה!) ---
    st.divider()
    st.subheader("🎯 סימולטור יעד: מה הציון הבא שלי?")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        target = st.slider("לאיזה ממוצע סופי אתה שואף?", 60, 100, 90)
    with col_s2:
        rem_w = st.number_input("כמה נ\"ז נותרו לך לסיום התואר?", 1.0, 160.0, 20.0)
    
    curr_sum = (df['ציון'] * df['משקל']).sum()
    needed = (target * (total_w + rem_w) - curr_sum) / rem_w
    
    if needed > 100:
        st.warning(f"כדי להגיע לממוצע {target}, תצטרך ממוצע של {needed:.2f} בקורסים שנותרו. זה נראה מאתגר! 💪")
    elif needed < 0:
        st.success(f"אתה כבר מעבר ליעד! גם אם תוציא ציונים נמוכים, הממוצע יישאר מעל {target}.")
    else:
        st.info(f"כדי להגיע ליעד של {target}, עליך להוציא ממוצע של **{needed:.2f}** בקורסים שנותרו.")

else:
    st.info("GradeMaster Pro מוכן לעבודה. הוסף קורס בתפריט הצד כדי להתחיל!")
