# app/admin.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from app.config import load_config, save_config, get_webhooks_config
from app.auth import require_admin, ensure_csrf, check_csrf

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, _=Depends(require_admin)):
    config = get_webhooks_config()
    repos = config.get("repos", {})
    secret = config.get("secret", "")
    csrf_token = ensure_csrf(request)
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "repos": repos,
        "secret": secret,
        "csrf_token": csrf_token,
    })

@router.post("/admin/add-repo")
async def add_repo(
    request: Request,
    repo_name: str = Form(...),
    csrf: str = Form(...),
    _=Depends(require_admin),
):
    check_csrf(request, csrf)
    config = load_config()
    repos = config.setdefault("repos", {})
    repos.setdefault(repo_name, [])
    save_config(config)
    return RedirectResponse("/admin", status_code=303)

@router.post("/admin/delete-repo")
async def delete_repo(
    request: Request,
    repo_name: str = Form(...),
    csrf: str = Form(...),
    _=Depends(require_admin),
):
    check_csrf(request, csrf)
    config = load_config()
    if repo_name in config.get("repos", {}):
        del config["repos"][repo_name]
        save_config(config)
    return RedirectResponse("/admin", status_code=303)

@router.post("/admin/add-url")
async def add_url(
    request: Request,
    repo_name: str = Form(...),
    webhook_url: str = Form(...),
    csrf: str = Form(...),
    _=Depends(require_admin),
):
    check_csrf(request, csrf)
    config = load_config()
    repos = config.setdefault("repos", {})
    urls = repos.setdefault(repo_name, [])
    if webhook_url not in urls:
        urls.append(webhook_url)
    save_config(config)
    return RedirectResponse("/admin", status_code=303)

@router.post("/admin/delete-url")
async def delete_url(
    request: Request,
    repo_name: str = Form(...),
    webhook_url: str = Form(...),
    csrf: str = Form(...),
    _=Depends(require_admin),
):
    check_csrf(request, csrf)
    config = load_config()
    urls = config.get("repos", {}).get(repo_name, [])
    if webhook_url in urls:
        urls.remove(webhook_url)
        save_config(config)
    return RedirectResponse("/admin", status_code=303)

@router.post("/admin/test-url")
async def test_url(
    request: Request,
    repo_name: str = Form(...),
    webhook_url: str = Form(...),
    csrf: str = Form(...),
    _=Depends(require_admin),
):
    check_csrf(request, csrf)
    from app.teams import send_to_teams
    try:
        await send_to_teams(
            webhook_url=webhook_url,
            title="🔧 Test webhook",
            pr_number=0,
            sender="admin-panel",
            branch_from="test-branch",
            branch_to="main",
            pr_url="https://github.com",
            repo=repo_name,
            labels="(ninguno)",
            milestone=None,
            merged=False
        )
    except Exception as e:
        print(f"[Admin] ERROR enviando test: {e}")
    return RedirectResponse("/admin", status_code=303)

@router.post("/admin/set-secret")
async def set_secret(
    request: Request,
    secret: str = Form(...),
    csrf: str = Form(...),
    _=Depends(require_admin),
):
    check_csrf(request, csrf)
    config = load_config()
    config["secret"] = secret
    save_config(config)
    return RedirectResponse("/admin", status_code=303)
