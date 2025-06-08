from fastapi import FastAPI
import logging
from dotenv import load_dotenv

import models
from database import engine
from routes import users, prescriptions, check_ins, llm

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prescription Management API", debug=True)


# Include routers
app.include_router(users.router)
app.include_router(prescriptions.router)
app.include_router(check_ins.router)
app.include_router(llm.router)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 