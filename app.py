import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# การตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Eimeria Maxima Tracker", layout="wide")

st.title("🔬 Eimeria maxima Micro Report System")
st.markdown("---")

# --- ส่วนที่ 1: ข้อมูลพื้นฐาน ---
col_head1, col_head2, col_head3 = st.columns(3)
with col_head1:
    area = st.text_input("Area / เขตพื้นที่", placeholder="เช่น ภาคกลาง")
with col_head2:
    farm_name = st.text_input("Farm / ชื่อฟาร์ม")
with col_head3:
    report_date = st.date_input("Date", datetime.now())

st.markdown("---")

# --- ส่วนที่ 2: การอัปโหลดรูปภาพ (ที่ขอมา!) ---
st.subheader("📸 Microscope Image Upload")
uploaded_file = st.file_uploader("เลือกรูปภาพ Oocyst หรือถ่ายรูปจากมือถือ", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Microscope Preview', use_container_width=True)
    st.success("อัปโหลดรูปภาพสำเร็จ!")

st.markdown("---")

# --- ส่วนที่ 3: ตารางกรอกข้อมูล (อิงตามไฟล์ Excel เดิมของคุณ) ---
st.subheader("Data Recording (No. 1 - No. 6)")

# สร้าง DataFrame เปล่าเพื่อรอรับค่า
rows = []
farm_houses = ["Farm 1", "Farm 2", "Farm 3"]

for farm in farm_houses:
    st.write(f"### {farm}")
    cols = st.columns(6) # สร้าง 6 คอลัมน์สำหรับ No. 1 - 6
    farm_data = {"Farm/House": farm}
    
    for i in range(1, 7):
        with cols[i-1]:
            st.caption(f"No. {i}")
            sm = st.number_input(f"S-M", min_value=0, step=1, key=f"sm_{farm}_{i}")
            lg = st.number_input(f"L", min_value=0, step=1, key=f"lg_{farm}_{i}")
            farm_data[f"No.{i}_SM"] = sm
            farm_data[f"No.{i}_L"] = lg
    rows.append(farm_data)

# --- ส่วนที่ 4: สรุปผลอัตโนมัติ ---
st.markdown("---")
if st.button("Generate Report & Analyze"):
    df_result = pd.DataFrame(rows)
    
    # คำนวณ Positive / Negative
    # Logic: ถ้าช่องใดช่องหนึ่ง (SM หรือ L) > 0 ถือว่าเป็น Positive
    def check_positive(row):
        values = [row[f"No.{i}_SM"] for i in range(1, 7)] + [row[f"No.{i}_L"] for i in range(1, 7)]
        return any(v > 0 for v in values)

    df_result['Status'] = df_result.apply(lambda r: "🔴 Positive" if check_positive(r) else "🟢 Negative", axis=1)
    
    st.subheader("📊 Summary Result")
    st.dataframe(df_result[['Farm/House', 'Status']], use_container_width=True)
    
    # ปุ่มดาวน์โหลด Data
    csv = df_result.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name=f"Eimeria_Report_{farm_name}_{report_date}.csv",
        mime='text/csv',
    )
