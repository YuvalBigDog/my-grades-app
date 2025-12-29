import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# הגדרות דף
st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

st.title("🎓 GradeMaster Pro | ניהול ציונים חכם")
st.markdown("---")

# אתחול רשימת הציונים בזיכרון (כדי שלא יימחקו ברענון)
if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# תפריט צדי להזנת נתונים
with st.sidebar:
    st.header("📝 הוספת מקצוע")
    with st.form("add_grade_form", clear_on_submit=True):
        name = st.text_input("שם המקצוע")
        grade = st.number_input("ציון (0-100)", min_value=0, max_value=100, value=90)
        weight = st.number_input("נקודות זכות (נ"ז)", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
        submitted = st.form_submit_button("הוסף למערכת")
        
        if submitted:
            if name:
                st.session_state.subjects.append({"מקצוע": name, "ציון": grade, "משקל": weight})
                st.toast(f"הוספת את {name}!")
            else:
                st.error("חובה להזין שם מקצוע")

    if st.button("🗑️ נקה את כל הנתונים"):
        st.session_state.subjects = []
        st.rerun()

# הצגת הנתונים והגרפים רק אם יש נתונים
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישובים
    total_weight = df['משקל'].sum()
    weighted_avg = (df['ציון'] * df['משקל']).sum() / total_weight
    
    # שורת מדדים עליונה
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("ממוצע משוקלל", f"{weighted_avg:.2f}")
    col_b.metric("סה\"כ נקודות זכות", f"{total_weight}")
    col_c.metric("מספר מקצועות", len(df))

    st.markdown("---")

    # חלוקה לטבלה וגרף
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 רשימת ציונים")
        st.dataframe(df, use_container_width=True)
        
        # כפתור הורדה ל-Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        st.download_button(
            label="📥 הורד דוח ל-Excel",
            data=output.getvalue(),
            file_name="my_grades_report.xlsx",
            mime="application/vnd.ms-excel"
        )

    with col2:
        st.subheader("📊 ניתוח ויזואלי (מתעדכן)")
        # יצירת הגרף - ברגע שמוסיפים ציון ה-DF משתנה והגרף נבנה מחדש
        fig = px.bar(
            df, 
            x="מקצוע", 
            y="ציון", 
            color="ציון",
            text="ציון",
            color_continuous_scale="RdYlGn", 
            range_y=[0, 110],
            labels={"ציון": "ציון סופי", "מקצוע": "שם הקורס"}
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # סימולטור יעד
    st.markdown("---")
    st.subheader("🎯 סימולטור יעד: כמה צריך לקבל?")
    
    c1, c2 = st.columns(2)
    with c1:
        target = st.slider("מה ממוצע היעד שלך?", min_value=60, max_value=100, value=90)
    with c2:
        rem_w = st.number_input("כמה נ"ז נשארו לך לסיום התואר/שנה?", min_value=1.0, value=10.0)

    current_sum = (df['ציון'] * df['משקל']).sum()
    req_grade = (target * (total_weight + rem_w) - current_sum) / rem_w
    
    if req_grade > 100:
        st.error(f"בשביל ממוצע {target} תצטרך להוציא {req_grade:.1f} בשאר הקורסים. זה בלתי אפשרי, אולי כדאי להוריד ציפיות? 🤔")
    elif req_grade < 55:
        st.success(f"מצבך מעולה! אתה צריך רק ממוצע {req_grade:.1f} בשאר הקורסים כדי להגיע ליעד.")
    else:
        st.info(f"כדי להגיע לממוצע {target}, אתה צריך להוציא ממוצע של **{req_grade:.1f}** בקורסים שנשארו.")

else:
    st.warning("👈 התחל להזין ציונים בתפריט הצדי כדי לראות את הגרפים והחישובים!")
