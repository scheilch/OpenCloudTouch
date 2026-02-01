"""Entry point for running soundtouch_bridge as module."""

from cloudtouch.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7777)
