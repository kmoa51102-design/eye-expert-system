from pathlib import Path

import pandas as pd

from app.rules import RULES, calculate_rule_statistics


DATASET_PATH = Path(__file__).resolve().parents[1] / 'dataset_300_eye_diseases.csv'
SYMPTOM_KEYS = (
    'PainlessBlurryVision',
    'AsymptomaticEarly',
    'NightVisionLoss',
    'TunnelVision',
    'RainbowHalos',
    'CentralDistortion',
    'Floaters',
)
DISEASE_LABELS = {
    'Glaucoma': '🟢 โรคต้อหิน',
    'AMD': '🟡 โรคจุดภาพชัดที่จอตาเสื่อม',
    'Diabetic_Retinopathy': '🔴 โรคเบาหวานขึ้นตา',
}
NO_RULE_DIAGNOSIS = 'ไม่พบโรคที่ตรงกับกฎ'


def load_dataset():
    if not DATASET_PATH.exists():
        from generate_dataset import generate_dataset

        generate_dataset()

    return pd.read_csv(DATASET_PATH)

def evaluate_patient(user_inputs: dict):
    df_dataset = load_dataset()
    symptoms = {key: int(bool(user_inputs.get(key, 0))) for key in SYMPTOM_KEYS}
    age = float(user_inputs['age'])
    sex = {'female': 'Female', 'male': 'Male'}.get(user_inputs.get('sex'))

    symptom_distance = sum(
        (df_dataset[key].astype(int) != value).astype(float)
        for key, value in symptoms.items()
    )
    age_range = max(float(df_dataset['Age'].max() - df_dataset['Age'].min()), 1.0)
    age_distance = (df_dataset['Age'].astype(float) - age).abs() / age_range * 0.25
    sex_distance = (
        (df_dataset['Sex'].astype(str) != sex).astype(float) * 0.25
        if sex
        else 0.0
    )
    distances = symptom_distance + age_distance + sex_distance
    closest_distance = float(distances.min())
    closest = df_dataset[distances <= closest_distance + 1e-9]

    votes = closest['Diagnosis'].value_counts()
    highest_vote = int(votes.max())
    winning_diseases = votes[votes == highest_vote].index.tolist()

    exact_symptom_matches = df_dataset
    for key, value in symptoms.items():
        exact_symptom_matches = exact_symptom_matches[
            exact_symptom_matches[key].astype(int) == value
        ]
    if exact_symptom_matches.empty:
        nearest_symptom_distance = symptom_distance.min()
        tie_break_matches = df_dataset[symptom_distance == nearest_symptom_distance]
    else:
        tie_break_matches = exact_symptom_matches

    tie_break_votes = tie_break_matches['Diagnosis'].value_counts()
    disease_order = {disease: index for index, disease in enumerate(DISEASE_LABELS)}
    winning_disease = max(
        winning_diseases,
        key=lambda disease: (
            int(tie_break_votes.get(disease, 0)),
            -disease_order[disease],
        ),
    )
    diagnosis = DISEASE_LABELS[winning_disease]
    dataset_matches = [
        {
            'disease': disease,
            'disease_th': DISEASE_LABELS[disease],
            'records': int(count),
            'percentage': round(float(count) / len(closest) * 100, 2),
        }
        for disease, count in votes.items()
    ]

    activated_rules = []
    disease_rule_confidence = {}
    for rule in RULES:
        if all(symptoms[key] == expected for key, expected in rule['conds'].items()):
            statistics = calculate_rule_statistics(df_dataset, rule)
            rule_confidence = statistics['confidence_pct'] / 100
            activated_rules.append({
                'rule_id': rule['id'],
                'disease_th': rule['disease_th'],
                'description': rule['desc'],
                **statistics,
            })
            disease_rule_confidence[rule['disease']] = max(
                disease_rule_confidence.get(rule['disease'], 0.0),
                rule_confidence,
            )

    cf_diseases = sorted(
        [
            {
                'disease': disease,
                'disease_th': DISEASE_LABELS[disease],
                'cf': round(confidence, 4),
            }
            for disease, confidence in disease_rule_confidence.items()
        ],
        key=lambda item: item['cf'],
        reverse=True,
    )
    final_cf = cf_diseases[0]['cf'] if cf_diseases else 0.0
    cf_winners = [
        disease for disease in cf_diseases
        if abs(disease['cf'] - final_cf) < 1e-9
    ]
    if final_cf > 0:
        cf_winning_disease = max(
            (disease['disease'] for disease in cf_winners),
            key=lambda disease: (
                int(tie_break_votes.get(disease, 0)),
                -disease_order[disease],
            ),
        )
        cf_diagnosis = DISEASE_LABELS[cf_winning_disease]
    else:
        cf_diagnosis = NO_RULE_DIAGNOSIS

    return {
        'primary_diagnosis': cf_diagnosis,
        'matched_record_count': len(closest),
        'match_distance': round(closest_distance, 3),
        'is_exact_match': closest_distance < 1e-9,
        'dataset_matches': dataset_matches,
        'dataset_result': {
            'primary_diagnosis': diagnosis,
            'disease': winning_disease,
            'confidence_pct': round(
                float(votes.get(winning_disease, 0)) / len(closest) * 100,
                2,
            ),
            'matched_record_count': len(closest),
            'matches': dataset_matches,
        },
        'cf_result': {
            'primary_diagnosis': cf_diagnosis,
            'final_cf': final_cf,
            'diseases': cf_diseases,
            'activated_rules': activated_rules,
        },
    }