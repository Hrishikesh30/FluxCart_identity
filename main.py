from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"Identity_recon is working"}