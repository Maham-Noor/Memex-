from fastapi import FastAPI

app = FastAPI(title="Memex Backend", version="0.1.0")

@app.get("/")
def read_root() -> dict:
    return {"status": "ok", "message": "Memex backend is running."}
