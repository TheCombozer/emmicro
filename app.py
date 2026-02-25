import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Eimeria Maxima Analysis Pro", layout="wide")

st.title("🔬 Eimeria maxima Micro Report (Pro Version)")
st.info("Logic: ผล Positive จะตัดสินจาก L Oocyst เท่านั้น | การแสดงผลแบบแยกบรรทัดต่อตัวอย่าง")

# --- ส่วนที่ 1: ข้อมูลทั่วไป ---
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        area = st.text_input("Area / เขตพื้นที่", "ภาคกลาง")
    with col2:
        report_date = st.date_input("Date", datetime.now())
    with col3:
        num_farms = st.number_input("จำนวนฟาร์ม", min_value=1, max_value=50, value=2)

# --- ส่วนที่ 2: ตั้งชื่อฟาร์มและรูปภาพ ---
st.subheader("🏠 Farm & Evidence")
farm_names = []
f_cols = st.columns(4)
for i in range(num_farms):
    with f_cols[i % 4]:
        name = st.text_input(f"ฟาร์มที่ {i+1}", f"Farm {i+1}", key=f"fn_{i}")
        farm_names.append(name)

uploaded_files = st.file_uploader("📸 อัปโหลดรูปภาพหลักฐาน", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
if uploaded_files:
    img_cols = st.columns(6)
    for i, file in enumerate(uploaded_files):
        with img_cols[i % 6]:
            st.image(Image.open(file), use_container_width=True)

st.markdown("---")

# --- ส่วนที่ 3: การกรอกข้อมูลแบบ Row-per-Sample (Professional) ---
st.subheader("📝 Sample Recording")
all_rows = []

for farm in farm_names:
    with st.expander(f"📥 บันทึกข้อมูล: {farm}", expanded=True):
        # สร้าง Header สำหรับการกรอกข้อมูล
        h1, h2, h3, h4 = st.columns([1, 1, 2, 2])
        h1.write("**Sample No.**")
        h2.write("**S-M Oocyst**")
        h3.write("**L Oocyst**")
        h4.write("**Result (Based on L)**")
        
        for i in range(1, 7): # ไก่ 6 ตัวต่อฟาร์ม
            c1, c2, c3, c4 = st.columns([1, 1, 2, 2])
            with c1:
                st.write(f"ตัวอย่างที่ {i}")
            with c2:
                sm = st.number_input(f"S-M", min_value=0, key=f"sm_{farm}_{i}", label_visibility="collapsed")
            with c3:
                lg = st.number_input(f"L", min_value=0, key=f"lg_{farm}_{i}", label_visibility="collapsed")
            
            # Logic: Positive เฉพาะ L Oocyst เท่านั้น
            status = "🔴 Positive" if lg > 0 else "🟢 Negative"
            with c4:
                if status == "🔴 Positive":
                    st.error(status)
                else:
                    st.success(status)
            
            all_rows.append({
                "Date": report_date,
                "Area": area,
                "Farm": farm,
                "Sample_No": i,
                "SM_Oocyst": sm,
                "L_Oocyst": lg,
                "Result": status
            })

# --- ส่วนที่ 4: รายงานสรุปผล ---
st.markdown("---")
if st.button("📊 Generate Professional Report"):
    df = pd.DataFrame(all_rows)
    
    # คำนวณภาพรวมรายฟาร์ม (ถ้าตัวอย่างใดตัวอย่างหนึ่งในฟาร์มนั้นมี L > 0)
    st.subheader("📋 Final Summary Report")
    
    # แสดงตารางแบบ Long Format
    st.dataframe(
        df.style.applymap(
            lambda x: 'background-color: #ffcccc' if x == "🔴 Positive" else '',
            subset=['Result']
        ),
        use_container_width=True,
        hide_index=True
    )
    
    # สรุปสถิติ
    total_pos_samples = (df['Result'] == "🔴 Positive").sum()
    st.metric("Total Positive Samples (Found L)", f"{total_pos_samples} จาก {len(df)} ตัวอย่าง")

    # ปุ่มดาวน์โหลด
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download Excel-Ready CSV",
        data=csv,
        file_name=f"Eimeria_Pro_Report_{report_date}.csv",
        mime='text/csv'
    )
