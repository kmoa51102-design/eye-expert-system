RULES = [
    {
        "id": "R1", "disease": "Glaucoma", "disease_th": "🟢 โรคต้อหิน",
        "conds": {'PainlessBlurryVision': 1, 'TunnelVision': 1, 'RainbowHalos': 1},
        "desc": "ตามัวลงเรื่อย ๆ + ลานสายตาแคบ + เห็นวงรุ้งรอบไฟ"
    },
    {
        "id": "R2", "disease": "Glaucoma", "disease_th": "🟢 โรคต้อหิน",
        "conds": {'PainlessBlurryVision': 1, 'TunnelVision': 1, 'CentralDistortion': 0, 'Floaters': 0},
        "desc": "ตามัวลงเรื่อย ๆ + ลานสายตาแคบ โดยไม่มีภาพกลางบิดเบี้ยวหรือจุดลอย"
    },
    {
        "id": "R3", "disease": "Glaucoma", "disease_th": "🟢 โรคต้อหิน",
        "conds": {'PainlessBlurryVision': 1, 'TunnelVision': 1, 'RainbowHalos': 1, 'AsymptomaticEarly': 1, 'NightVisionLoss': 1},
        "desc": "ตามัวลงเรื่อย ๆ + ลานสายตาแคบ + เห็นวงรุ้งรอบไฟ ร่วมกับอาการระยะแรกและการมองกลางคืนลดลง"
    },
    {
        "id": "R4", "disease": "AMD", "disease_th": "🟡 โรคจุดภาพชัดที่จอตาเสื่อม",
        "conds": {'PainlessBlurryVision': 1, 'AsymptomaticEarly': 1, 'NightVisionLoss': 1, 'CentralDistortion': 1},
        "desc": "ตามัวโดยไม่เจ็บ + อาการระยะแรก + มองกลางคืนลดลง + ภาพตรงกลางบิดเบี้ยว"
    },
    {
        "id": "R5", "disease": "AMD", "disease_th": "🟡 โรคจุดภาพชัดที่จอตาเสื่อม",
        "conds": {'PainlessBlurryVision': 1, 'CentralDistortion': 1, 'TunnelVision': 0, 'RainbowHalos': 0},
        "desc": "ตามัวโดยไม่เจ็บ + ภาพตรงกลางบิดเบี้ยว โดยไม่มีลานสายตาแคบหรือวงรุ้งรอบไฟ"
    },
    {
        "id": "R6", "disease": "AMD", "disease_th": "🟡 โรคจุดภาพชัดที่จอตาเสื่อม",
        "conds": {'PainlessBlurryVision': 1, 'CentralDistortion': 1, 'NightVisionLoss': 1, 'Floaters': 0},
        "desc": "ตามัวโดยไม่เจ็บ + ภาพตรงกลางบิดเบี้ยว + มองกลางคืนลดลง โดยไม่มีจุดหรือเส้นลอย"
    },
    {
        "id": "R7", "disease": "Diabetic_Retinopathy", "disease_th": "🔴 โรคเบาหวานขึ้นตา",
        "conds": {'PainlessBlurryVision': 1, 'AsymptomaticEarly': 1, 'NightVisionLoss': 1, 'Floaters': 1},
        "desc": "ตามัวโดยไม่เจ็บ + อาการระยะแรก + มองกลางคืนลดลง + เห็นจุดดำหรือเส้นหยากไย่ลอย"
    },
    {
        "id": "R8", "disease": "Diabetic_Retinopathy", "disease_th": "🔴 โรคเบาหวานขึ้นตา",
        "conds": {'PainlessBlurryVision': 1, 'Floaters': 1, 'TunnelVision': 0, 'RainbowHalos': 0, 'CentralDistortion': 0},
        "desc": "ตามัวโดยไม่เจ็บ + เห็นจุดหรือเส้นลอย โดยไม่มีสัญญาณเด่นของต้อหินหรือ AMD"
    },
    {
        "id": "R9", "disease": "Diabetic_Retinopathy", "disease_th": "🔴 โรคเบาหวานขึ้นตา",
        "conds": {'PainlessBlurryVision': 1, 'Floaters': 1, 'NightVisionLoss': 1, 'CentralDistortion': 0},
        "desc": "ตามัวโดยไม่เจ็บ + เห็นจุดหรือเส้นลอย + มองกลางคืนลดลง โดยไม่มีภาพตรงกลางบิดเบี้ยว"
    }
]


def matching_dataset_records(dataset, rule):
    matches = dataset
    for symptom, expected in rule["conds"].items():
        matches = matches[matches[symptom].astype(int) == expected]
    return matches


def calculate_rule_statistics(dataset, rule):
    if dataset.empty:
        raise ValueError("Cannot calculate rule statistics from an empty dataset")

    matches = matching_dataset_records(dataset, rule)
    support_pct = len(matches) / len(dataset) * 100
    confidence_pct = (
        matches["Diagnosis"].eq(rule["disease"]).mean() * 100
        if len(matches)
        else 0.0
    )
    return {
        "support_pct": round(support_pct, 2),
        "confidence_pct": round(confidence_pct, 2),
    }