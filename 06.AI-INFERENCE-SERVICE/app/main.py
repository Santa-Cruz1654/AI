from fastapi import FastAPI


app = FastAPI(
    title="AI Inference Service",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "AI Inference Service is running"}