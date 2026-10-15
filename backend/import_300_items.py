import pandas as pd
import numpy as np
import pymysql

# 1. สร้าง Dataset สมบูรณ์ 300 รายการ
np.random.seed(42)
n_samples = 100

def generate_disease_data(disease_name, primary_symptom_col, id_start):
    data = []
    for i in range(n_samples):
        patient_id = id_start + i
        age = int(np.random.randint(50, 85))
        sex = np.random.choice(['Male', 'Female'])
        
        # อาการร่วมพื้นฐาน (80-90% โอกาสที่จะมีอาการ)
        painless_blurry = np.random.choice([1, 0], p=[0.9, 0.1])
        asymptomatic = np.random.choice([1, 0], p=[0.8, 0.2])
        night_vision = np.random.choice([1, 0], p=[0.8, 0.2])
        
        # อาการเฉพาะโรค
        tunnel_vision = 1 if disease_name == 'Glaucoma' else np.random.choice([1, 0], p=[0.05, 0.95])
        rainbow_halos = 1 if disease_name == 'Glaucoma' and np.random.rand() > 0.15 else np.random.choice([1, 0], p=[0.05, 0.95])
        
        central_distortion = 1 if disease_name == 'AMD' else np.random.choice([1, 0], p=[0.05, 0.95])
        
        floaters = 1 if disease_name == 'Diabetic_Retinopathy' else np.random.choice([1, 0], p=[0.05, 0.95])
        
        data.append((
            patient_id, age, sex,
            painless_blurry, asymptomatic, night_vision,
            tunnel_vision, rainbow_halos, central_distortion, floaters,
            disease_name
        ))
    return data

# รวมข้อมูล 3 โรค โรคละ 100 รายการ = 300 รายการ
all_data = []
all_data.extend(generate_disease_data('Glaucoma', 'tunnel_vision', 101))
all_data.extend(generate_disease_data('AMD', 'central_distortion', 201))
all_data.extend(generate_disease_data('Diabetic_Retinopathy', 'floaters', 301))

# 2. บันทึกลง MySQL
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',  # ⚠️ ปรับรหัสผ่าน XAMPP ของคุณถ้ามี
    database='eye_expert_system',
    charset='utf8mb4'
)

cursor = conn.cursor()
cursor.execute("TRUNCATE TABLE dataset_records;") # ล้างตารางก่อนยัดข้อมูลใหม่

sql = """
INSERT INTO dataset_records 
(patient_id, age, sex, painless_blurry_vision, asymptomatic_early, night_vision_loss, tunnel_vision, rainbow_halos, central_distortion, floaters, diagnosis)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

cursor.executemany(sql, all_data)
conn.commit()
conn.close()

print(f"✅ เพิ่มข้อมูลครบถ้วน {len(all_data)} รายการ ลงตาราง dataset_records เรียบร้อยแล้ว!")