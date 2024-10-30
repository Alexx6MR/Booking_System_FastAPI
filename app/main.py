from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select


from models import Classroom
from db.seed import seed
from db.dbCondig import create_db_and_tables, SessionDep





@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    create_db_and_tables()
    seed()
    yield
    # Clean up the ML models and release the resources
 

app = FastAPI(lifespan=lifespan)
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def root(request: Request, session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100,) -> list[Classroom]:
    classrooms = session.exec(select(Classroom).offset(offset).limit(limit)).all()
    if not classrooms:
        raise HTTPException(status_code=404, detail="Classrooms not found")

    return templates.TemplateResponse("index.html", {"request": request, "classroomsList": classrooms if len(classrooms) > 0 else []})

