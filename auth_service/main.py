from fastapi import FastAPI, Body
import uvicorn
from pydantic import BaseModel

app = FastAPI()

class RegisterUser(BaseModel):
    uuid: str
    pswd: str
    hash: int
    role: str
    
class CredsUser(BaseModel):
    uuid: str
    pswd: str

@app.post('/register')
def register():
    user = RegisterUser(uuid='f47ac10b-58cc-4372-a567-0e02b2c3d479', pswd='0A#v!4sGq8Zx%2Tt6B9u', 
                hash=hash('f47ac10b-58cc-4372-a567-0e02b2c3d479'), role='patient')
    return user
    
@app.post('/login/')
def login(creds: CredsUser):
    user = RegisterUser(uuid=creds.uuid, pswd=creds.pswd, hash=hash(creds.pswd), role='patient')
    
    return {
        'user': user,
        'creds': creds
    }
    
if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)