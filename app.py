import streamlit as st
import pandas as pd
import plotly.express as px

# הגדרות דף
st.set_page_config(page_title="Your Grades Calculator", page_icon="🎓", layout="wide")

st.title("🎓 Your Grades Calculator")

# אתחול הנתונים
if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# --- תפריט צד להזנה וגיבוי ---
with st.sidebar:
    st.header("➕ Add New Course")
    name = st.text_input("Course Name")
    grade = st.number_input("Grade", 0, 100, 85)
    weight = st.number_input("Credits (נ\"ז)", 1.0, 10.0, 2.0, 0.5)
    year = st.selectbox("Year:", ["Year A", "Year B", "Year C", "Year D"])
    
    if st.button("Add to List"):
        if name:
            st.session_state.subjects.append({
                "Course": name, "Year": year, "Grade": float(grade), "Credits": float(weight)
            })
            st.rerun()
    
    st.divider()
    st.header("💾 Save & Load")
    if st.session_state.subjects:
        df_download = pd.DataFrame(st.session_state.subjects)
        csv = df_download.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Download Backup (CSV)", data=csv, file_name='my_grades.csv', mime='text/csv')
    
    uploaded_file = st.file_uploader("📤 Upload Backup", type="csv")
    if uploaded_file is not None:
        st.session_state.subjects = pd.read_csv(uploaded_file).to_dict('records')
        st.rerun()

    if st.button("🗑️ Clear All Data"):
        st.session_state.subjects = []
        st.rerun()

# --- חישובים ותצוגה ---
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

    # תצוגת מחוונים
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Average", value=f"{current_avg:.2f}", delta=f"{delta_val:+.2f}" if delta_val is not None else None)
    col2.metric(label="Total Credits", value=f"{total_w:.1f}")
    col3.metric(label="Last Grade", value=f"{df.iloc[-1]['Grade']:.0f}")

    st.divider()

    # --- פיתצ'ר עריכה ומחיקה יחידנית ---
    st.subheader("📋 My Courses (Edit or Delete)")
    
    # אפשרות 1: עריכה ישירה בטבלה
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    # אם המשתמש שינה משהו בטבלה, נעדכן את הזיכרון
    if not edited_df.equals(df):
        st.session_state.subjects = edited_df.to_dict('records')
        st.rerun()

    # אפשרות 2: מחיקת קורס ספציפי דרך תפריט
    st.write("---")
    col_del1, col_del2 = st.columns([3, 1])
    course_to_delete = col_del1.selectbox("Select a course to remove:", df['Course'].unique())
    if col_del2.button("❌ Remove Course"):
        st.session_state.subjects = [s for s in st.session_state.subjects if s['Course'] != course_to_delete]
        st.success(f"Removed {course_to_delete}")
        st.rerun()

    # גרפים וניבוי
    st.divider()
    st.subheader("📈 Yearly Comparison")
    year_stats = df.groupby('Year').apply(
        lambda x: (x['Grade'].astype(float) * x['Credits']).sum() / x['Credits'].sum()
    ).reset_index()
    year_stats.columns = ['Year', 'Average']
    fig = px.bar(year_stats, x='Year', y='Average', color='Year', text_auto='.2f')
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("🎯 Target Predictor")
    c1, c2 = st.columns(2)
    target = c1.number_input("Target Average:", 60.0, 100.0, 90.0)
    future_w = c2.number_input("Remaining Credits:", 1.0, 150.0, 10.0)
    needed = (target * (total_w + future_w) - (df['Grade'].astype(float) * df['Credits']).sum()) / future_w
    
    if needed > 100:
        st.error(f"Required Average: {needed:.2f} (Hard target!)")
    else:
        st.info(f"To reach {target:.2f}, you need an average of **{needed:.2f}** in future exams.")

else:
    st.info("Your list is empty. Add a course or upload a backup file to start.")
