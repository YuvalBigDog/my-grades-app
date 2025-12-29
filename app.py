import streamlit as st
import pandas as pd
import plotly.express as px

# 1. שינוי כותרת האתר (מה שמופיע בלשונית)
st.set_page_config(page_title="Your Grades Calculator", page_icon="🎓", layout="wide")

# 2. שינוי הכותרת הראשית באתר
st.title("🎓 Your Grades Calculator")

if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# --- תפריט צד ---
with st.sidebar:
    st.header("➕ Add Course")
    name = st.text_input("Course Name")
    grade = st.number_input("Grade", 0, 100, 85)
    weight = st.number_input("Credits", 1.0, 10.0, 2.0, 0.5)
    year = st.selectbox("Year:", ["Year A", "Year B", "Year C", "Year D"])
    
    if st.button("Add to List"):
        if name:
            st.session_state.subjects.append({
                "Course": name, "Year": year, "Grade": float(grade), "Credits": float(weight)
            })
            st.rerun()

    st.divider()
    st.header("💾 Backup")
    if st.session_state.subjects:
        csv = pd.DataFrame(st.session_state.subjects).to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Download CSV", data=csv, file_name='grades.csv')
    
    uploaded_file = st.file_uploader("📤 Upload CSV", type="csv")
    if uploaded_file:
        st.session_state.subjects = pd.read_csv(uploaded_file).to_dict('records')
        st.rerun()

# --- הצגת נתונים ומחיקה ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישוב ממוצע ומגמה
    total_w = df['Credits'].sum()
    current_avg = (df['Grade'] * df['Credits']).sum() / total_w
    
    delta_val = None
    if len(df) > 1:
        prev_df = df.iloc[:-1]
        prev_avg = (prev_df['Grade'] * prev_df['Credits']).sum() / prev_df['Credits'].sum()
        delta_val = current_avg - prev_avg

    # מחוונים למעלה
    c1, c2, c3 = st.columns(3)
    c1.metric("Average", f"{current_avg:.2f}", delta=f"{delta_val:+.2f}" if delta_val else None)
    c2.metric("Credits", f"{total_w:.1f}")
    c3.metric("Last Grade", f"{df.iloc[-1]['Grade']:.0f}")

    st.divider()

    # פיצ'ר המחיקה והעריכה שביקשת
    st.subheader("📝 Edit or Delete Courses")
    
    # טבלה שניתן לערוך בה ציונים ישירות
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="editor")
    
    if not edited_df.equals(df):
        st.session_state.subjects = edited_df.to_dict('records')
        st.rerun()

    # מחיקה יחידנית לפי שם
    st.write("---")
    col_sel, col_btn = st.columns([3, 1])
    to_delete = col_sel.selectbox("Select course to remove:", df['Course'].unique())
    if col_btn.button("❌ Remove Selected"):
        st.session_state.subjects = [s for s in st.session_state.subjects if s['Course'] != to_delete]
        st.rerun()

    # גרף וניבוי
    st.subheader("📈 Yearly Comparison")
    year_stats = df.groupby('Year').apply(lambda x: (x['Grade'] * x['Credits']).sum() / x['Credits'].sum()).reset_index()
    year_stats.columns = ['Year', 'Avg']
    st.plotly_chart(px.bar(year_stats, x='Year', y='Avg', color='Year', text_auto='.2f'))

    st.divider()
    st.subheader("🎯 Target Predictor")
    t_avg = st.slider("Target:", 60.0, 100.0, 90.0)
    f_w = st.number_input("Future Credits:", 1.0, 100.0, 10.0)
    needed = (t_avg * (total_w + f_w) - (df['Grade'] * df['Credits']).sum()) / f_w
    st.info(f"You need an average of **{needed:.2f}** to reach your target.")

else:
    st.info("No courses yet. Add one from the sidebar!")
