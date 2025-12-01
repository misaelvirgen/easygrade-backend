from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "EasyGrade backend running"}
