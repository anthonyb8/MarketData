from fastapi import FastAPI
import app.routes as routes

app = FastAPI()

# Include routes
app.include_router(routes.router)
