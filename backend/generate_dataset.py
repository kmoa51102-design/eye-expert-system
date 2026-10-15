from pathlib import Path

import numpy as np
import pandas as pd


BACKEND_DIR = Path(__file__).resolve().parent
SOURCE_PATH = BACKEND_DIR / 'full_df.csv'
OUTPUT_PATH = BACKEND_DIR / 'dataset_300_eye_diseases.csv'


def generate_dataset():
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f'ไม่พบไฟล์ข้อมูลต้นทาง: {SOURCE_PATH}')

    df_raw = pd.read_csv(SOURCE_PATH)
    rng = np.random.default_rng(42)
    groups = [
        (df_raw[df_raw['G'] == 1].head(100), 'Glaucoma'),
        (df_raw[df_raw['A'] == 1].head(100), 'AMD'),
        (df_raw[df_raw['D'] == 1].head(100), 'Diabetic_Retinopathy'),
    ]
    dataset = []

    for cases, disease in groups:
        if len(cases) < 100:
            raise ValueError(f'ข้อมูลสำหรับ {disease} มีน้อยกว่า 100 ราย')

        for _, row in cases.iterrows():
            dataset.append({
                'Patient_ID': int(row['ID']),
                'Age': int(row['Patient Age']) if pd.notnull(row['Patient Age']) else 50,
                'Sex': str(row['Patient Sex']),
                'PainlessBlurryVision': int(rng.random() < 0.90),
                'AsymptomaticEarly': int(rng.random() < 0.85),
                'NightVisionLoss': int(rng.random() < 0.80),
                'TunnelVision': int(rng.random() < (0.85 if disease == 'Glaucoma' else 0.05)),
                'RainbowHalos': int(rng.random() < (0.70 if disease == 'Glaucoma' else 0.03)),
                'CentralDistortion': int(rng.random() < (0.88 if disease == 'AMD' else 0.04)),
                'Floaters': int(rng.random() < (0.82 if disease == 'Diabetic_Retinopathy' else 0.06)),
                'Diagnosis': disease,
            })

    pd.DataFrame(dataset).to_csv(OUTPUT_PATH, index=False)
    return OUTPUT_PATH


if __name__ == '__main__':
    generate_dataset()
    print('Created dataset_300_eye_diseases.csv (300 records).')