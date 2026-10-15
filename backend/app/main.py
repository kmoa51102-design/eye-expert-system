from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.inference import evaluate_patient


class AssessmentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=1, le=120)
    sex: Literal['female', 'male', 'other']
    painless_blurry_vision: bool = Field(alias='PainlessBlurryVision')
    asymptomatic_early: bool = Field(alias='AsymptomaticEarly')
    night_vision_loss: bool = Field(alias='NightVisionLoss')
    tunnel_vision: bool = Field(alias='TunnelVision')
    rainbow_halos: bool = Field(alias='RainbowHalos')
    central_distortion: bool = Field(alias='CentralDistortion')
    floaters: bool = Field(alias='Floaters')

    def symptoms(self):
        return {
            'PainlessBlurryVision': int(self.painless_blurry_vision),
            'AsymptomaticEarly': int(self.asymptomatic_early),
            'NightVisionLoss': int(self.night_vision_loss),
            'TunnelVision': int(self.tunnel_vision),
            'RainbowHalos': int(self.rainbow_halos),
            'CentralDistortion': int(self.central_distortion),
            'Floaters': int(self.floaters),
        }


app = FastAPI(title='Eye Expert System API')


@app.get('/api/health')
def health_check():
    return {'status': 'ok'}


@app.post('/api/diagnose')
def diagnose(payload: AssessmentRequest):
    try:
        result = evaluate_patient({
            **payload.symptoms(),
            'age': payload.age,
            'sex': payload.sex,
        })
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return {
        'patient': {
            'name': payload.name,
            'age': payload.age,
            'sex': payload.sex,
        },
        **result,
    }