import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות דף רחב
st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

st.title("🎓 GradeMaster Pro - ניהול אקדמי מלא")

# אתחול נתונים
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
    if st.button("🗑️ איפוס כל הנתונים"):
        st.session_state.subjects = []
        st.rerun()

# --- הצגת הנתונים ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישובים כלליים
    total_w = df['משקל'].sum()
    total_avg = (df['ציון'] * df['משקל']).sum() / total_w
    
    # שורת מדדים עליונה
    m1, m2 = st.columns(2)
    m1.metric("🎓 ממוצע תואר כולל", f"{total_avg:.2f}")
    m2.metric("📜 סך נ\"ז שנצברו", f"{total_w:.1f}")

    st.divider()

    # טבלת פירוט הקורסים (מה שביקשת להחזיר)
    st.subheader("📋 רשימת הקורסים המלאה")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # גרף השוואה בין שנים
    st.subheader("📊 השוואת ממוצעים בין השנים")
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['משקל']).sum() / x['משקל'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']
    year_stats['ממוצע שנתי'] = year_stats['ממוצע שנתי'].round(2)
    
    fig = px.bar(year_stats, x='שנה', y='ממוצע שנתי', color='שנה', 
                 text_auto='.2f', title="התקדמות הממוצע לפי שנה")
    fig.update_layout(yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)

    # --- סימולטור יעד (חזר לבקשתך!) ---
    st.divider()
    st.subheader("🎯 סימולטור יעד: מה הציון הבא שלי?")
    
    s1, s2 = st.columns(2)
    with s1:
        target = st.slider("לאיזה ממוצע סופי אתה שואף?", 60, 100, 90)
    with s2:
        rem_w = st.number_input("כמה נ\"ז נותרו לך לסיום התואר?", 1.0, 160.0, 20.0)
    
    curr_sum = (df['ציון'] * df['משקל']).sum()
    needed = (target * (total_w + rem_w) - curr_sum) / rem_w
    
    if needed > 100:
        st.warning(f"כדי להגיע ל-{target}, תצטרך ממוצע של {needed:.2f}. זה ידרוש פוש רציני! 💪")
    elif needed < 0:
        st.success(f"אתה כבר מעל היעד! הממוצע שלך בטוח מעל {target}.")
    else:
        st.info(f"כדי להגיע ליעד של {target}, עליך להוציא ממוצע של **{needed:.2f}** בקורסים שנותרו.")

else:
    st.info("GradeMaster Pro מוכן. הוסף את הקורס הראשון שלך בתפריט הצד!")
