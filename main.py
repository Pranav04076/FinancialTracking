import os

import uvicorn

if __name__ == "__main__":
    # Hosting platforms such as Render provide the public port in PORT.
    # Keep 8000 as the local-development fallback.
    uvicorn.run("app.app:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
