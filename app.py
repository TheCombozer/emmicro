import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Eimeria Maxima Analysis Pro", layout="wide")

st.title("🔬 Eimeria maxima Micro Report")

# --- ส่วนที่ 1: ข้อมูลทั่วไป ---
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        area = st.text_input("Area / เขตพื้นที่", "ภาคกลาง")
    with col2:
        report_date = st.date_input("Date", datetime.now())
    with col3:
        num_farms = st.number_input("จำนวนฟาร์ม", min_value=1, max_value=50, value=3)

# --- ส่วนที่ 2: ตั้งชื่อฟาร์มและรูปภาพ ---
farm_names = []
f_cols = st.columns(4)
for i in range(num_farms):
    with f_cols[i % 4]:
        name = st.text_input(f"ฟาร์มที่ {i+1}", f"Farm {i+1}", key=f"fn_{i}")
        farm_names.append(name)

uploaded_files = st.file_uploader("📸 อัปโหลดรูปภาพหลักฐาน", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

st.markdown("---")

# --- ส่วนที่ 3: การกรอกข้อมูล (แยก Row เพื่อความง่ายในการลงข้อมูล) ---
all_rows = []
for farm in farm_names:
    with st.expander(f"📥 บันทึกข้อมูล: {farm}", expanded=True):
        cols = st.columns(6)
        for i in range(1, 7):
            with cols[i-1]:
                st.markdown(f"**ตัวอย่างที่ {i}**")
                sm = st.number_input(f"S-M", min_value=0, key=f"sm_{farm}_{i}")
                lg = st.number_input(f"L", min_value=0, key=f"lg_{farm}_{i}")
                
                all_rows.append({
                    "Farm": farm,
                    "Sample": i,
                    "S-M": sm,
                    "L": lg
                })

# --- ส่วนที่ 4: สรุปผลรายงาน (ปรับเป็น Column ตามคำขอ) ---
st.markdown("---")
if st.button("📊 Generate Pro Summary"):
    raw_df = pd.DataFrame(all_rows)
    
    # สร้างตาราง Summary แบบแนวนอน (Wide Format)
    # ใช้ Pivot Table เพื่อกาง Sample No. ออกเป็น Column
    summary_df = raw_df.pivot(index='Farm', columns='Sample', values=['S-M', 'L'])
    
    # ปรับชื่อ Column ให้ดู Pro (เช่น L1, SM1, L2, SM2...)
    summary_df.columns = [f"{val}{col}" for val, col in summary_df.columns]
    summary_df = summary_df.reset_index()

    # คำนวณสถานะ Positive (เช็คเฉพาะ L1 - L6)
    l_cols = [c for c in summary_df.columns if c.startswith('L')]
    summary_df['Total_L'] = summary_df[l_cols].sum(axis=1)
    summary_df['Result'] = summary_df['Total_L'].apply(lambda x: "🔴 Positive" if x > 0 else "🟢 Negative")

    st.subheader("📋 ตารางสรุปผลรายฟาร์ม (Summary Report)")
    
    # ตกแต่งตารางก่อนแสดงผล
    st.dataframe(
        summary_df.style.applymap(
            lambda x: 'background-color: #ffcccc; color: red; font-weight: bold' if x == "🔴 Positive" else '',
            subset=['Result']
        ),
        use_container_width=True,
        hide_index=True
    )

    # สรุปภาพรวม
    pos_farms = (summary_df['Total_L'] > 0).sum()
    st.info(f"💡 สรุปภาพรวม: ตรวจทั้งหมด {num_farms} ฟาร์ม | พบเชื้อ (L Oocyst) ทั้งหมด {pos_farms} ฟาร์ม")

    # ปุ่มดาวน์โหลด
    csv = summary_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download Summary CSV", csv, "Summary_Report.csv", "text/csv")
