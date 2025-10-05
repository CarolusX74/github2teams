# app/auth.py
import os
import secrets
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
router = APIRouter()

def get_env_user() -> str:
    return os.environ.get("ADMIN_USER", "admin")

def get_env_pass() -> str:
    return os.environ.get("ADMIN_PASS", "change_me")

def ensure_csrf(request: Request) -> str:
    if "csrf" not in request.session:
        request.session["csrf"] = secrets.token_urlsafe(32)
    return request.session["csrf"]

def require_admin(request: Request):
    if not request.session.get("admin_auth"):
        # Si querés redirigir en vez de 401:
        # raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, detail="Login required")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")

def check_csrf(request: Request, token: str):
    session_token = request.session.get("csrf")
    if not session_token or not token or token != session_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSRF token invalid")

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == get_env_user() and password == get_env_pass():
        request.session["admin_auth"] = True
        ensure_csrf(request)
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Usuario o contraseña incorrectos."},
        status_code=401,
    )

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
