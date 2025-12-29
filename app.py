import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GradeMaster Pro", page_icon="🎓")

st.title("🎓 GradeMaster Pro - מחשבון ציונים חכם")

# אתחול רשימת הציונים בזיכרון
if 'subjects' not in st.session_state:
    st.session_state.subjects = []

# תפריט צדי להוספת מקצועות
with st.sidebar:
    st.header("הוספת מקצוע חדש")
    name = st.text_input("שם המקצוע")
    grade = st.number_input("ציון", min_value=0, max_value=100, value=90)
    weight = st.number_input("נקודות זכות / משקל", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
    
    if st.button("הוסף למערכת"):
        if name:
            st.session_state.subjects.append({"מקצוע": name, "ציון": grade, "משקל": weight})
            st.success(f"הוספת את {name} בהצלחה!")
        else:
            st.error("נא להזין שם מקצוע")

    if st.button("נקה הכל"):
        st.session_state.subjects = []
        st.rerun()

# הצגת הנתונים
if st.session_state.subjects:
    df = pd.DataFrame(st.session_state.subjects)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("פירוט ציונים")
        st.table(df)
        
    with col2:
        total_weight = df['משקל'].sum()
        weighted_avg = (df['ציון'] * df['משקל']).sum() / total_weight
        st.metric("ממוצע נוכחי", f"{weighted_avg:.2f}")

    # גרף התפלגות
    st.subheader("ניתוח ויזואלי")
    fig = px.bar(df, x="מקצוע", y="ציון", color="ציון", color_continuous_scale="RdYlGn", range_y=[0, 100])
    st.plotly_chart(fig)

    # --- הפיצ'ר החדש: סימולטור יעד ---
    st.divider()
    st.subheader("🎯 סימולטור יעד (מה אני צריך לקבל?)")
    
    target_avg = st.slider("מה ממוצע היעד שלך?", min_value=int(weighted_avg), max_value=100, value=90)
    remaining_weight = st.number_input("כמה נקודות זכות (נ"ז) נשארו לך לסיום?", min_value=1.0, value=5.0)
    
    # חישוב הציון הנדרש
    # (current_weighted_sum + required_grade * remaining_weight) / (total_weight + remaining_weight) = target_avg
    current_sum = (df['ציון'] * df['משקל']).sum()
    total_new_weight = total_weight + remaining_weight
    required_score = (target_avg * total_new_weight - current_sum) / remaining_weight
    
    if required_score > 100:
        st.warning(f"כדי להגיע לממוצע {target_avg}, תצטרך לקבל {required_score:.1f} במבחנים הבאים. זה נראה קצת קשה... 😅")
    elif required_score < 0:
        st.success(f"אתה כבר מעל היעד! גם אם תקבל 0 במבחנים הבאים, הממוצע שלך יהיה גבוה מ-{target_avg}.")
    else:
        st.info(f"כדי להגיע לממוצע {target_avg}, עליך להוציא ממוצע של **{required_score:.1f}** בשאר המקצועות.")

else:
    st.info("המתן להזנת נתונים... המחשבון ריק כרגע.")
