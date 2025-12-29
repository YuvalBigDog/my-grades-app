import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות דף ועיצוב
st.set_page_config(page_title="GradeMaster Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    h1 { color: #1f77b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 GradeMaster Pro | ניהול ציונים חכם")

# אזור הזנת הנתונים
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"קורס": "סטטיסטיקה", "שנה": "א", "נז": 4.0, "ציון": 80},
        {"קורס": "מתמטיקה א", "שנה": "א", "נז": 2.0, "ציון": 88}
    ])

edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "שנה": st.column_config.SelectboxColumn("שנה", options=["א", "ב"], required=True),
        "נז": st.column_config.NumberColumn("נ\"ז", min_value=1.0, max_value=10.0, step=0.5),
        "ציון": st.column_config.NumberColumn("ציון", min_value=0, max_value=100)
    }
)

# הגדרת משתני החישוב מראש כדי למנוע שגיאות
avg_a, avg_b, total_avg = 0.0, 0.0, 0.0
total_credits_all = 0.0
current_weighted_sum = 0.0

if not edited_df.empty and (edited_df['ציון'] > 0).any():
    df = edited_df.copy()
    df['weighted'] = df['נז'] * df['ציון']
    
    # חישובים
    total_credits_all = df['נז'].sum()
    current_weighted_sum = df['weighted'].sum()
    total_avg = current_weighted_sum / total_credits_all if total_credits_all > 0 else 0
    
    avg_a = df[df['שנה'] == 'א']['weighted'].sum() / df[df['שנה'] == 'א']['נז'].sum() if df[df['שנה'] == 'א']['נז'].sum() > 0 else 0
    avg_b = df[df['שנה'] == 'ב']['weighted'].sum() / df[df['שנה'] == 'ב']['נז'].sum() if df[df['שנה'] == 'ב']['נז'].sum() > 0 else 0

    # תצוגת מדדים
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 ממוצע שנה א'", f"{avg_a:.2f}")
    diff = avg_b - avg_a if avg_a > 0 and avg_b > 0 else 0
    col2.metric("📈 ממוצע שנה ב'", f"{avg_b:.2f}", delta=f"{diff:+.2f}" if diff != 0 else None)
    col3.metric("🏆 ממוצע כללי", f"{total_avg:.2f}", f"סה\"כ {total_credits_all} נ\"ז")

# --- מחשבון ניבוי ---
st.divider()
st.subheader("🔮 מחשבון ניבוי: איזה ציון אני צריך?")
p_col1, p_col2 = st.columns(2)

with p_col1:
    target_avg = st.number_input("מה הממוצע שאתה שואף אליו?", min_value=1.0, max_value=100.0, value=88.0)
    next_exam_credits = st.number_input("כמה נ\"ז המבחן הקרוב?", min_value=1.0, max_value=10.0, value=4.0)

if total_credits_all > 0:
    new_total_credits = total_credits_all + next_exam_credits
    required_grade = ((target_avg * new_total_credits) - current_weighted_sum) / next_exam_credits

    with p_col2:
        st.write("### התוצאה שלך:")
        if required_grade > 100:
            st.error(f"אתה צריך **{required_grade:.1f}**. זה מעל 100, אולי כדאי לשפר קורסים קודמים.")
        elif required_grade < 0:
            st.success("אתה כבר שם! גם עם ציון 0 תעבור את הממוצע המבוקש.")
        else:
            st.info(f"עליך לקבל במבחן הקרוב ציון של: **{required_grade:.1f}**")