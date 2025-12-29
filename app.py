import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pilpilonet", page_icon="🎓", layout="wide")

st.title("🎓 pililonet - ניהול ומגמות")

if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# --- תפריט צד ---
with st.sidebar:
    st.header("➕ הוספת קורס")
    name = st.text_input("שם הקורס")
    grade = st.number_input("ציון", 0, 100, 85)
    weight = st.number_input("נקודות זכות (נ\"ז)", 1.0, 10.0, 2.0, 0.5)
    year = st.selectbox("שנה:", ["שנה א'", "שנה ב'", "שנה ג'", "שנה ד'"])
    
    if st.button("הוסף לרשימה"):
        if name:
            st.session_state.subjects.append({
                "קורס": name, "שנה": year, "ציון": float(grade), "נ\"ז": float(weight)
            })
            st.rerun()
    
    st.divider()
    st.header("💾 שמירה וטעינה")
    if st.session_state.subjects:
        df_download = pd.DataFrame(st.session_state.subjects)
        csv = df_download.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 הורד גיבוי (CSV)", data=csv, file_name='my_grades.csv', mime='text/csv')
    
    uploaded_file = st.file_uploader("📤 טען גיבוי קיים", type="csv")
    if uploaded_file is not None:
        st.session_state.subjects = pd.read_csv(uploaded_file).to_dict('records')
        st.rerun()

    if st.button("🗑️ נקה הכל"):
        st.session_state.subjects = []
        st.rerun()

# --- חישוב המדדים והחיצים ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישוב ממוצע נוכחי
    total_w = df['נ\"ז'].sum()
    current_avg = (df['ציון'] * df['נ\"ז']).sum() / total_w
    
    # חישוב המגמה (השוואה לממוצע שהיה לפני הקורס האחרון)
    delta_val = None
    if len(df) > 1:
        prev_df = df.iloc[:-1] # כל הקורסים חוץ מהאחרון
        prev_avg = (prev_df['ציון'] * prev_df['נ\"ז']).sum() / prev_df['נ\"ז'].sum()
        delta_val = current_avg - prev_avg

    # תצוגת המדדים למעלה
    st.subheader("📊 מצב אקדמי נוכחי")
    col1, col2, col3 = st.columns(3)
    
    # הצגת הממוצע עם החץ (Delta)
    if delta_val is not None:
        col1.metric(label="🎓 ממוצע כולל", value=f"{current_avg:.2f}", delta=f"{delta_val:+.2f}")
    else:
        col1.metric(label="🎓 ממוצע כולל", value=f"{current_avg:.2f}")
        
    col2.metric(label="📜 סך נ\"ז", value=f"{total_w:.1f}")
    
    # הציון האחרון שהוזן
    last_grade = df.iloc[-1]['ציון']
    col3.metric(label="📝 ציון אחרון", value=f"{last_grade:.0f}")

    st.divider()
    
    # טבלת קורסים
    st.subheader("📋 רשימת הקורסים שלי")
    display_df = df.copy()
    display_df['ציון'] = display_df['ציון'].map(lambda x: f"{x:.2f}")
    st.dataframe(display_df[["קורס", "שנה", "ציון", "נ\"ז"]], use_container_width=True)

    # גרף השוואת שנים
    st.subheader("📈 השוואה בין שנים")
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['נ\"ז']).sum() / x['נ\"ז'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']
    fig = px.bar(year_stats, x='שנה', y='ממוצע שנתי', color='שנה', text_auto='.2f', 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(yaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)

    # סימולטור ניבוי
    st.divider()
    st.subheader("🎯 סימולטור ניבוי")
    c1, c2 = st.columns(2)
    target = c1.number_input("ממוצע יעד סופי:", 60.0, 100.0, 90.0)
    future_w = c2.number_input("נ\"ז שנותרו לתואר:", 1.0, 150.0, 10.0)
    needed = (target * (total_w + future_w) - (df['ציון'] * df['נ\"ז']).sum()) / future_w
    
    if needed > 100:
        st.error(f"לא ריאלי: תצטרך ממוצע של {needed:.2f} כדי להגיע ליעד.")
    else:
        st.info(f"כדי להגיע לממוצע {target:.2f}, עליך להוציא ממוצע של **{needed:.2f}** בקורסים שנותרו.")
else:
    st.info("הזן קורסים בתפריט הצד כדי לראות את הנתונים והמגמות.")


