from fastapi import FastAPI
import uvicorn
from app.api.auth import router as auth_router


app = FastAPI()
app.include_router(auth_router)
 
if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)