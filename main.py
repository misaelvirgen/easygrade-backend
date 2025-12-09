from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.health import router as health_router
from routes.grade import router as grade_router
from routes.upload_pdf import router as upload_pdf_router
from routes.google_classroom import router as google_router
from routes.canvas import router as canvas_router
from routes import rubric
from routes import upload_rubric
from routes.stripe_webhook import router as stripe_webhook_router   # <-- ADD THIS

app = FastAPI(title="EasyGrade Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
app.include_router(health_router)

# API routes
app.include_router(grade_router, prefix="/api")
app.include_router(upload_pdf_router, prefix="/api")
app.include_router(google_router, prefix="/api")
app.include_router(canvas_router, prefix="/api")
app.include_router(rubric.router, prefix="/api/rubric")
app.include_router(upload_rubric.router, prefix="/api/upload")

# Stripe webhook route 
app.include_router(stripe_webhook_router)
