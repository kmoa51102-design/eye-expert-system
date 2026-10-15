import argparse
import pandas as pd
import pymysql
from pathlib import Path

from app.rules import RULES, calculate_rule_statistics

parser = argparse.ArgumentParser()
parser.add_argument(
    '--rules-only',
    action='store_true',
    help='Synchronize rules_records without changing dataset_records',
)
args = parser.parse_args()

# ตั้งค่าการเชื่อมต่อ MySQL (ปรับ password ตาม XAMPP/phpMyAdmin ของคุณ ถ้าไม่มีให้ใส่ '')
DATABASE_NAME = 'eye_expert_system'
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # ⚠️ ปรับรหัสผ่าน MySQL ตรงนี้
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conn.select_db(DATABASE_NAME)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dataset_records (
            record_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            age INT,
            sex VARCHAR(20),
            painless_blurry_vision TINYINT,
            asymptomatic_early TINYINT,
            night_vision_loss TINYINT,
            tunnel_vision TINYINT,
            rainbow_halos TINYINT,
            central_distortion TINYINT,
            floaters TINYINT,
            diagnosis VARCHAR(50)
        )
    """)
    cursor.execute("SHOW COLUMNS FROM dataset_records LIKE 'record_id'")
    if cursor.fetchone() is None:
        cursor.execute("""
            ALTER TABLE dataset_records
            DROP PRIMARY KEY,
            ADD COLUMN record_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rules_records (
            rule_id VARCHAR(10) PRIMARY KEY,
            disease VARCHAR(50),
            disease_th VARCHAR(255),
            description TEXT,
            painless_blurry_vision TINYINT,
            asymptomatic_early TINYINT,
            night_vision_loss TINYINT,
            tunnel_vision TINYINT,
            rainbow_halos TINYINT,
            central_distortion TINYINT,
            floaters TINYINT,
            support_pct DECIMAL(5, 2) NOT NULL DEFAULT 0,
            confidence_pct DECIMAL(5, 2) NOT NULL DEFAULT 0
        )
    """)

    for column in ("support_pct", "confidence_pct"):
        cursor.execute(f"SHOW COLUMNS FROM rules_records LIKE '{column}'")
        if cursor.fetchone() is None:
            cursor.execute(
                f"ALTER TABLE rules_records "
                f"ADD COLUMN {column} DECIMAL(5, 2) NOT NULL DEFAULT 0"
            )

    # 1. ย้ายข้อมูล Dataset 300 รายการ
    csv_path = Path(__file__).resolve().parent / 'dataset_300_eye_diseases.csv'
    if not csv_path.exists():
        raise FileNotFoundError(
            f"ไม่พบไฟล์ {csv_path} (รัน generate_dataset.py ก่อน)"
        )
    df = pd.read_csv(csv_path)
    if not args.rules_only:
        cursor.execute("TRUNCATE TABLE dataset_records;") # ล้างข้อมูลเก่า
        for _, row in df.iterrows():
            sql = """INSERT INTO dataset_records 
                     (patient_id, age, sex, painless_blurry_vision, asymptomatic_early, night_vision_loss, tunnel_vision, rainbow_halos, central_distortion, floaters, diagnosis)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                int(row['Patient_ID']), int(row['Age']), str(row['Sex']),
                int(row['PainlessBlurryVision']), int(row['AsymptomaticEarly']), int(row['NightVisionLoss']),
                int(row['TunnelVision']), int(row['RainbowHalos']), int(row['CentralDistortion']),
                int(row['Floaters']), str(row['Diagnosis'])
            ))
        print("✅ นำเข้าข้อมูล Dataset 300 ชุดลง MySQL สำเร็จแล้ว!")
    else:
        print("ℹ️ คงข้อมูลในตาราง dataset_records ไว้ตามเดิม")

    # 2. ย้ายข้อมูล Rules (กฎ)
    cursor.execute("DELETE FROM rules_records")
    for rule in RULES:
        statistics = calculate_rule_statistics(df, rule)
        symptoms = (
            'PainlessBlurryVision',
            'AsymptomaticEarly',
            'NightVisionLoss',
            'TunnelVision',
            'RainbowHalos',
            'CentralDistortion',
            'Floaters',
        )
        sql = """INSERT INTO rules_records 
                 (rule_id, disease, disease_th, description, painless_blurry_vision, asymptomatic_early, night_vision_loss, tunnel_vision, rainbow_halos, central_distortion, floaters, support_pct, confidence_pct)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (
            rule['id'],
            rule['disease'],
            rule['disease_th'],
            rule['desc'],
            *(rule['conds'].get(symptom) for symptom in symptoms),
            statistics['support_pct'],
            statistics['confidence_pct'],
        ))
    print("✅ นำเข้าชุดข้อมูลกฎ (Rules) ลง MySQL สำเร็จแล้ว!")

    conn.commit()
    conn.close()
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาดในการนำเข้าข้อมูล: {e}")
    raise