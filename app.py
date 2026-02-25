import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Eimeria Maxima Pro", layout="wide")

st.title("🔬 Eimeria maxima Micro Report (Customizable)")
st.info("ระบุจำนวนฟาร์มและชื่อฟาร์มด้านล่าง ก่อนกรอกข้อมูลตัวอย่าง")

# --- ส่วนที่ 1: ข้อมูลทั่วไปและตั้งค่าฟาร์ม ---
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        area = st.text_input("Area / เขตพื้นที่", "ภาคกลาง")
    with col2:
        report_date = st.date_input("Date", datetime.now())
    with col3:
        # ส่วนสำคัญ: กำหนดจำนวนฟาร์มได้เอง
        num_farms = st.number_input("จำนวนฟาร์มที่ตรวจ", min_value=1, max_value=20, value=3)

st.markdown("---")

# --- ส่วนที่ 2: ตั้งชื่อฟาร์มและอัปโหลดรูป ---
farm_names = []
st.subheader("🏠 Farm Names & Reference Images")
f_cols = st.columns(num_farms)
for i in range(num_farms):
    name = f_cols[i].text_input(f"ชื่อฟาร์มที่ {i+1}", f"Farm {i+1}")
    farm_names.append(name)

uploaded_file = st.file_uploader("📸 อัปโหลดรูปภาพหลักฐาน (Microscope Image)", type=['jpg', 'jpeg', 'png'])
if uploaded_file:
    st.image(Image.open(uploaded_file), width=300, caption="ตัวอย่างเชื้อที่พบ")

st.markdown("---")

# --- ส่วนที่ 3: ตารางกรอกข้อมูลแบบ Dynamic ---
st.subheader("📝 Data Entry (No. 1 - No. 6)")
all_data = []

for farm in farm_names:
    with st.expander(f"📥 กรอกข้อมูลสำหรับ: {farm}", expanded=True):
        row_data = {"Farm/House": farm}
        cols = st.columns(6)
        
        # เก็บผลบวกแยกรายฟาร์มเพื่อสรุป Status
        farm_is_positive = False
        
        for i in range(1, 7):
            with cols[i-1]:
                st.markdown(f"**ตัวอย่าง {i}**")
                sm = st.number_input(f"S-M", min_value=0, key=f"sm_{farm}_{i}")
                lg = st.number_input(f"L", min_value=0, key=f"lg_{farm}_{i}")
                
                row_data[f"No.{i}_SM"] = sm
                row_data[f"No.{i}_L"] = lg
                
                if sm > 0 or lg > 0:
                    farm_is_positive = True
        
        row_data["Status"] = "🔴 Positive" if farm_is_positive else "🟢 Negative"
        all_data.append(row_data)

# --- ส่วนที่ 4: แสดงตารางสรุปทั้งหมด ---
st.markdown("---")
if st.button("📊 Generate Full Summary Report"):
    df = pd.DataFrame(all_data)
    
    # จัดลำดับคอลัมน์ให้สวยงาม (ย้าย Status ไปไว้ท้ายสุด)
    cols = list(df.columns)
    cols.append(cols.pop(cols.index('Status')))
    df = df[cols]
    
    st.subheader("📋 ตารางสรุปผลการตรวจวิเคราะห์")
    
    # แสดงตารางแบบ Interactive
    st.dataframe(df.style.applymap(
        lambda x: 'color: red; font-weight: bold' if x == "🔴 Positive" else ('color: green' if x == "🟢 Negative" else ''),
        subset=['Status']
    ), use_container_width=True)
    
    # คำนวณภาพรวม
    pos_count = (df['Status'] == "🔴 Positive").sum()
    st.metric("ภาพรวมการพบเชื้อ", f"{pos_count} / {num_farms} ฟาร์ม", delta="พบเชื้อ" if pos_count > 0 else "ปกติ", delta_color="inverse")

    # ปุ่มดาวน์โหลด
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download Full Report (CSV)",
        data=csv,
        file_name=f"Eimeria_Full_Report_{report_date}.csv",
        mime='text/csv'
    )
