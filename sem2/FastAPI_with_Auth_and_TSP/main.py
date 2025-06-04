from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.api.auth import router as auth_router
from app.api.tsp import router as tsp_router
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="User Authentication and TSP API",
    openapi_tags=[
        {"name": "auth", "description": "Authentication operations"},
        {"name": "tsp", "description": "Traveling Salesman Problem operations"}
    ]
)

# Явное определение OAuth2 схемы
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")
app.dependency_overrides[OAuth2PasswordBearer] = oauth2_scheme

# Кастомизация OpenAPI для принудительного указания tokenUrl
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="API for user authentication and TSP",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "scopes": {},
                    "tokenUrl": "/auth/login/"
                }
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to User Authentication and TSP API"}

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(tsp_router, prefix="/tsp", tags=["tsp"])