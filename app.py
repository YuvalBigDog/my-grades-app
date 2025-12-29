import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓", layout="wide")

st.title("🎓 GradeMaster Pro - השוואת שנים והתקדמות")

if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# --- תפריט צד להזנה ---
with st.sidebar:
    st.header("הוספת מקצוע")
    name = st.text_input("שם המקצוע")
    grade = st.number_input("ציון", min_value=0, max_value=100, value=85)
    weight = st.number_input("נקודות זכות (נ\"ז)", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
    
    # הפיצ'ר שביקשת - בחירת שנה
    year = st.selectbox("שייך לשנה:", ["שנה א'", "שנה ב'", "שנה ג'", "שנה ד'"])
    
    if st.button("הוסף למערכת"):
        if name:
            st.session_state.subjects.append({"שנה": year, "מקצוע": name, "ציון": grade, "משקל": weight})
            st.success(f"הוספת את {name} ל{year}")
        else:
            st.error("נא להזין שם מקצוע")

    if st.button("איפוס נתונים"):
        st.session_state.subjects = []
        st.rerun()

# --- הצגת נתונים וניתוח ---
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    # חישוב ממוצעים לפי שנה להשוואה
    year_stats = df.groupby('שנה').apply(
        lambda x: (x['ציון'] * x['משקל']).sum() / x['משקל'].sum()
    ).reset_index()
    year_stats.columns = ['שנה', 'ממוצע שנתי']

    # שורת מדדים עליונה
    col_a, col_b = st.columns(2)
    with col_a:
        total_avg = (df['ציון'] * df['משקל']).sum() / df['משקל'].sum()
        st.metric("ממוצע תואר כולל", f"{total_avg:.2f}")
    with col_b:
        best_year = year_stats.loc[year_stats['ממוצע שנתי'].idxmax(), 'שנה']
        st.metric("השנה החזקה ביותר", best_year)

    st.divider()

    # גרף השוואה בין שנים - זה מה שחיפשת!
    st.subheader("📊 השוואת ממוצעים בין השנים")
    fig_years = px.bar(year_stats, x='שנה', y='ממוצע שנתי', 
                       text_auto='.2f', color='שנה',
                       title="ממוצע משוקלל לפי שנה",
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_years.update_layout(yaxis_range=[0, 105])
    st.plotly_chart(fig_years, use_container_width=True)

    # פירוט בטבלה
    st.subheader("📋 פירוט מלא")
    st.dataframe(df.sort_values("שנה"), use_container_width=True)

    # סימולטור יעד
    st.divider()
    st.subheader("🎯 סימולטור יעד לתואר")
    target = st.slider("לאיזה ממוצע סופי אתה שואף?", 60, 100, 90)
    rem_w = st.number_input("כמה נ\"ז נותרו לך לסיום התואר?", 1.0, 160.0, 20.0)
    
    curr_sum = (df['ציון'] * df['משקל']).sum()
    needed = (target * (df['משקל'].sum() + rem_w) - curr_sum) / rem_w
    
    if needed > 100:
        st.warning(f"כדי להגיע ל-{target}, תצטרך ממוצע של {needed:.1f}. זה ידרוש מאמץ אדיר!")
    else:
        st.info(f"כדי להגיע ליעד, עליך להוציא ממוצע של **{needed:.1f}** בקורסים שנותרו.")

else:
    st.info("המערכת מחכה שתזין את המקצוע הראשון שלך בתפריט הצד!")
