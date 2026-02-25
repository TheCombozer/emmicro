import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Eimeria Maxima Pro - Multi Photo", layout="wide")

st.title("🔬 Eimeria maxima Micro Report (Multi-Image Support)")
st.info("ระบุจำนวนฟาร์ม ชื่อฟาร์ม และอัปโหลดภาพหลักฐานได้ไม่จำกัดจำนวน")

# --- ส่วนที่ 1: ข้อมูลทั่วไป ---
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        area = st.text_input("Area / เขตพื้นที่", "ภาคกลาง")
    with col2:
        report_date = st.date_input("Date", datetime.now())
    with col3:
        num_farms = st.number_input("จำนวนฟาร์มที่ตรวจ", min_value=1, max_value=50, value=3)

st.markdown("---")

# --- ส่วนที่ 2: ตั้งชื่อฟาร์ม ---
st.subheader("🏠 Farm Setup")
farm_names = []
# ปรับให้แสดงช่องกรอกชื่อฟาร์มแบบ Grid เพื่อไม่ให้ยาวเกินไป
cols_per_row = 4
rows_needed = (num_farms // cols_per_row) + (1 if num_farms % cols_per_row != 0 else 0)

for r in range(rows_needed):
    f_cols = st.columns(cols_per_row)
    for c in range(cols_per_row):
        idx = r * cols_per_row + c
        if idx < num_farms:
            name = f_cols[c].text_input(f"ฟาร์มที่ {idx+1}", f"Farm {idx+1}", key=f"fn_{idx}")
            farm_names.append(name)

st.markdown("---")

# --- ส่วนที่ 3: อัปโหลดรูปภาพได้หลายภาพ (The Highlight!) ---
st.subheader("📸 Microscope Image Gallery")
uploaded_files = st.file_uploader(
    "ลากไฟล์มาวางที่นี่ หรือกดเลือกรูปภาพ (เลือกได้หลายไฟล์พร้อมกัน)", 
    type=['jpg', 'jpeg', 'png'], 
    accept_multiple_files=True # เปิดให้เลือกได้หลายภาพ
)

if uploaded_files:
    # แสดงรูปภาพที่อัปโหลดในรูปแบบ Grid
    img_cols = st.columns(4) 
    for i, file in enumerate(uploaded_files):
        with img_cols[i % 4]:
            img = Image.open(file)
            st.image(img, caption=f"Image {i+1}", use_container_width=True)
    st.success(f"อัปโหลดสำเร็จทั้งหมด {len(uploaded_files)} รูป")

st.markdown("---")

# --- ส่วนที่ 4: ตารางกรอกข้อมูล ---
st.subheader("📝 Data Entry (No. 1 - No. 6)")
all_data = []

for farm in farm_names:
    with st.expander(f"📥 บันทึกข้อมูล: {farm}", expanded=False): # ปิดไว้ก่อนเพื่อความสะอาดตา
        row_data = {"Farm/House": farm}
        cols = st.columns(6)
        
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

# --- ส่วนที่ 5: สรุปผลรายงานแบบละเอียด ---
st.markdown("---")
if st.button("📊 Generate Full Summary Report"):
    df = pd.DataFrame(all_data)
    
    # คำนวณค่าสถิติ
    pos_total = (df['Status'] == "🔴 Positive").sum()
    neg_total = (df['Status'] == "🟢 Negative").sum()

    # แสดงผล Highlight
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Farms", num_farms)
    m2.metric("Positive Case", pos_total, delta=f"{pos_total} farms", delta_color="inverse")
    m3.metric("Negative Case", neg_total)

    # แสดงตารางสรุป
    st.subheader("📋 Detailed Summary Table")
    # ปรับแต่งการแสดงผลตาราง
    st.dataframe(df, use_container_width=True)
    
    # ส่วนของไฟล์ดาวน์โหลด
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name=f"Eimeria_Report_{report_date}.csv",
        mime='text/csv'
    )
