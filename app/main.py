from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from db.seed import seed
from db.dbConfig import create_db_and_tables, SessionDep

from routes.auth import auth_router
from routes.classroom import classroom_router
from routes.user import user_router

# Defines the lifespan of the application, creating database tables and seeding data during startup, and cleaning up resources during shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    create_db_and_tables()
    seed()
    yield
    # Clean up the ML models and release the resources
 
# Defines the app object and static folder.
app = FastAPI(lifespan=lifespan)
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Adds CORS middleware to allow requests from any origin, with credentials, and all methods and headers.(NOT Important )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_global_context(request: Request, call_next):
    # Añadir datos al contexto que estará disponible para todas las peticiones
    request.state.global_context = {
        "app_name": "Booking System",
        "year": 2024,
        "is_logged_in": request.cookies.get("session_token") is not None,  # Ejemplo: verificar si el usuario está autenticado
        "user_id": request.cookies.get("user_id", 0)
    }
    response = await call_next(request)
    return response


# Defines the root endpoint that redirects users to the /classrooms page.
@app.get("/")
def root()-> None:
    return RedirectResponse(url="/classrooms")

@app.get("/about")
async def about(request: Request):
    global_context = request.state.global_context
    return templates.TemplateResponse("pages/about_page.html", {"request": request, "is_logged_in": global_context["is_logged_in"], "user_id": global_context["user_id"]})

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("pages/404_page.html", {"request": request}, status_code=404)


# Includes the all the routers in the app.
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(classroom_router, prefix="/classrooms", tags=["classrooms"])
app.include_router(user_router, prefix="/user", tags=["users"])

