import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

# אתחול ה-LocalStorage
local_storage = LocalStorage()

st.title("🎓 GradeMaster Pro - שמירה מקומית קבועה")
st.write("הנתונים נשמרים על המכשיר שלך ולא נמחקים ברענון!")

# פונקציה לטעינת נתונים מהזיכרון של המכשיר
def load_data():
    saved_data = local_storage.getItem("user_grades")
    if saved_data:
        return pd.DataFrame(saved_data)
    return pd.DataFrame(columns=["קורס", "שנה", "ציון", "נ\"ז"])

# טעינת הנתונים הקיימים
df = load_data()

# --- תפריט צד ---
with st.sidebar:
    st.header("➕ הוספת קורס")
    name = st.text_input("שם הקורס")
    grade = st.number_input("ציון", 0, 100, 85)
    weight = st.number_input("נקודות זכות (נ\"ז)", 1.0, 10.0, 2.0, 0.5)
    year = st.selectbox("שנה:", ["שנה א'", "שנה ב'", "שנה ג'", "שנה ד'"])
    
    if st.button("שמור במכשיר 💾"):
        if name:
            new_row = {"קורס": name, "שנה": year, "ציון": float(grade), "נ\"ז": float(weight)}
            # הוספה ל-DataFrame הקיים
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            # שמירה פיזית בזיכרון של הדפדפן
            local_storage.setItem("user_grades", df.to_dict(orient="records"))
            st.success(f"הקורס {name} נשמר לצמיתות!")
            st.rerun()
        else:
            st.error("נא להזין שם קורס")

    st.divider()
    if st.button("🗑️ מחק הכל מהמכשיר"):
        local_storage.deleteAll()
        st.rerun()

# --- תצוגת נתונים ---
if not df.empty:
    # וידוא פורמט מספרים (2 ספרות אחרי הנקודה)
    df['ציון'] = pd.to_numeric(df['ציון']).round(2)
    df['נ\"ז'] = pd.to_numeric(df['נ\"ז']).round(1)
    
    total_w = df['נ\"ז'].sum()
    weighted_avg = (df['ציון'] * df['נ\"ז']).sum() / total_w
    
    col1, col2 = st.columns(2)
    col1.metric("🎓 ממוצע כולל", f"{weighted_avg:.2f}")
    col2.metric("📜 סך נ\"ז", f"{total_w}")

    st.divider()
    st.subheader("📋 הקורסים השמורים שלך")
    st.dataframe(df[["קורס", "שנה", "ציון", "נ\"ז"]], use_container_width=True)

    # גרף השוואה
    st.subheader("📊 השוואה בין שנים")
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['נ\"ז']).sum() / x['נ\"ז'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']
    fig = px.bar(year_stats, x='שנה', y='ממוצע שנתי', color='שנה', text_auto='.2f')
    st.plotly_chart(fig, use_container_width=True)

    # סימולטור ניבוי
    st.divider()
    st.subheader("🎯 ניבוי ציון")
    c1, c2 = st.columns(2)
    target = c1.number_input("ממוצע יעד:", 60.0, 100.0, 90.0)
    future_w = c2.number_input("נ\"ז שנותרו:", 1.0, 100.0, 10.0)
    needed = (target * (total_w + future_w) - (df['ציון'] * df['נ\"ז']).sum()) / future_w
    st.info(f"עליך להוציא ממוצע של **{needed:.2f}** במבחנים הקרובים.")

else:
    st.info("אין נתונים שמורים במכשיר זה. הוסף קורס כדי להתחיל!")
