from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware  # 👈
from app.config import get_webhooks_for_repo, get_webhooks_config, WEBHOOK_SECRET
from app.teams import send_to_teams
from app.auth import router as auth_router  # 👈

import hmac
import hashlib
import os
import re

app = FastAPI()

# 🔐 Session cookie para login del panel
SESSION_SECRET = os.environ.get("SESSION_SECRET", "change_this_session_secret")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax", https_only=False)

ALLOWED_ACTIONS = {"opened", "reopened", "closed"}

def get_active_secret() -> bytes:
    try:
        config = get_webhooks_config()
        panel_secret = config.get("secret")
        if panel_secret:
            return panel_secret.encode()
    except Exception as e:
        print(f"[Webhook] No se pudo cargar secret del panel: {e}")
    return WEBHOOK_SECRET

def verify_signature(payload: bytes, signature: str) -> bool:
    secret = get_active_secret()
    if not secret or not signature:
        print("[Webhook] Secret vacío o firma ausente")
        return False
    expected_hash = hmac.new(secret, msg=payload, digestmod=hashlib.sha256).hexdigest()
    expected = f"sha256={expected_hash}"
    valid = hmac.compare_digest(expected, signature)
    if not valid:
        print(f"[Webhook] Firma inválida.\nEsperado: {expected}\nRecibido: {signature}")
    return valid

@app.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None)
):
    body = await request.body()
    print(f"[Webhook] Headers: {x_github_event} - {x_hub_signature_256}")

    if not verify_signature(body, x_hub_signature_256):
        print("[Webhook] Firma inválida")
        return JSONResponse({"detail": "Firma no válida"}, status_code=401)

    payload = await request.json()
    print(f"[Webhook] Payload recibido:\n{payload}")
    repo = payload.get("repository", {}).get("full_name", "unknown")
    webhooks = get_webhooks_for_repo(repo)
    if not webhooks:
        return JSONResponse({"detail": "No Teams webhook configured for this repo."}, status_code=404)

    if x_github_event == "pull_request":
        action = payload.get("action", "")
        if action not in ALLOWED_ACTIONS:
            return JSONResponse({"detail": f"Acción ignorada: {action}"}, status_code=200)
        if action == "closed" and not payload.get("pull_request", {}).get("merged", False):
            return JSONResponse({"detail": "PR cerrado sin merge. Ignorado."}, status_code=200)

        sender = payload.get("sender", {}).get("login", "unknown")
        pr = payload.get("pull_request", {})
        pr_title = pr.get("title", "")
        pr_url = pr.get("html_url", "")
        pr_branch = pr.get("head", {}).get("ref", "")
        pr_base = pr.get("base", {}).get("ref", "")
        pr_number = pr.get("number", 0)
        is_merged = pr.get("merged", False)

        labels = pr.get("labels", [])
        label_names = ", ".join(label["name"] for label in labels) if labels else ""

        milestone_obj = pr.get("milestone")
        milestone = milestone_obj.get("title") if milestone_obj else "(ninguno)"

        for url in webhooks:
            await send_to_teams(
                webhook_url=url,
                title=pr_title,
                pr_number=pr_number,
                sender=sender,
                branch_from=pr_branch,
                branch_to=pr_base,
                pr_url=pr_url,
                repo=repo,
                labels=label_names,
                milestone=milestone,
                merged=is_merged
            )

    elif x_github_event == "push":
        commits = payload.get("commits", [])
        base_ref = payload.get("ref", "").replace("refs/heads/", "")
        compare_url = payload.get("compare", "")
        pusher = payload.get("pusher", {}).get("name", "unknown")

        for commit in commits:
            message = commit.get("message", "").lower()
            if message.startswith("merge pull request"):
                match = re.search(r"#(\d+)", message)
                pr_number = int(match.group(1)) if match else 0
                pr_title = commit.get("message", "").strip().split("\n")[0]
                is_merged = True

                for url in webhooks:
                    await send_to_teams(
                        webhook_url=url,
                        title=pr_title,
                        pr_number=pr_number,
                        sender=pusher,
                        branch_from="(merge)",
                        branch_to=base_ref,
                        pr_url=compare_url,
                        repo=repo,
                        labels="-",
                        milestone=None,
                        merged=is_merged
                    )
                break
    else:
        print(f"[Webhook] Evento ignorado: {x_github_event}")
        return JSONResponse({"detail": f"Evento ignorado: {x_github_event}"}, status_code=200)

    print("[Webhook] Notificación enviada correctamente.")
    return {"detail": "Notificación enviada a Teams."}

# Routers
from app.admin import router as admin_router
app.include_router(auth_router)
app.include_router(admin_router)
