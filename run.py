from fastapi import FastAPI

app = FastAPI()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.entrypoints.main_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
