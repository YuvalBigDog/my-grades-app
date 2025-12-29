import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות דף
st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

st.title("🎓 GradeMaster Pro - ניהול אקדמי מלא")

if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# --- תפריט צד (הזנה) ---
with st.sidebar:
    st.header("➕ הוספת קורס חדש")
    name = st.text_input("שם הקורס")
    grade = st.number_input("ציון", min_value=0, max_value=100, value=85)
    weight = st.number_input("נקודות זכות (נ\"ז)", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
    year = st.selectbox("שייך לשנה:", ["שנה א'", "שנה ב'", "שנה ג'", "שנה ד'"])
    
    if st.button("הוסף למערכת"):
        if name:
            st.session_state.subjects.append({
                "שנה": year, 
                "קורס": name, 
                "ציון": float(grade), 
                "משקל": float(weight)
            })
            st.success(f"הוספת את {name} בהצלחה!")
        else:
            st.error("נא להזין שם קורס")

    st.divider()
    if st.button("🗑️ איפוס נתונים"):
        st.session_state.subjects = []
        st.rerun()

# --- הצגת הנתונים ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישובים
    total_w = df['משקל'].sum()
    total_avg = (df['ציון'] * df['משקל']).sum() / total_w
    
    # שורת מדדים
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("🎓 ממוצע תואר כולל", f"{total_avg:.2f}")
    col_m2.metric("📜 סך נ\"ז שנצברו", f"{total_w:.1f}")

    st.divider()

    # 1. טבלת קורסים מפורטת (מה שביקשת להחזיר למרכז)
    st.subheader("📋 רשימת הקורסים המלאה")
    # עיגול ציונים בטבלה
    df_styled = df.copy()
    df_styled['ציון'] = df_styled['ציון'].map('{:,.2f}'.format)
    df_styled['משקל'] = df_styled['משקל'].map('{:,.1f}'.format)
    st.dataframe(df_styled, use_container_width=True)

    st.divider()

    # 2. השוואת שנים
    st.subheader("📊 השוואת ממוצעים בין השנים")
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['משקל']).sum() / x['משקל'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']
    
    fig = px.bar(year_stats, x='שנה', y='ממוצע שנתי', color='שנה', 
                 text_auto='.2f', title="איך הממוצע שלך משתנה?")
    fig.update_layout(yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)

    # 3. מחשבון ניבוי ציון (סימולטור יעד)
    st.divider()
    st.subheader("🎯 סימולטור ניבוי: מה הציון הבא שלי?")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        target = st.slider("לאיזה ממוצע סופי אתה שואף?", 60, 100, 90)
    with col_s2:
        rem_w = st.number_input("נ\"ז של המבחנים הקרובים/שנותרו:", 1.0, 160.0, 10.0)
    
    curr_sum = (df['ציון'] * df['משקל']).sum()
    needed = (target * (total_w + rem_w) - curr_sum) / rem_w
    
    if needed > 100:
        st.warning(f"כדי להגיע ל-{target}, תצטרך ממוצע של {needed:.2f}. זה דורש פוש רציני!")
    elif needed < 0:
        st.success(f"אתה כבר מעל היעד! הממוצע שלך יישאר מעל {target} גם עם ציונים נמוכים.")
    else:
        st.info(f"כדי להגיע לממוצע {target}, עליך להוציא ממוצע של **{needed:.2f}** במבחנים הקרובים.")

else:
    st.info("GradeMaster Pro מוכן. הוסף קורס בתפריט הצד כדי להתחיל!")
