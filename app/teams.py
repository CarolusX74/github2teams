import httpx

async def send_to_teams(
    webhook_url: str,
    title: str,
    pr_number: int,
    sender: str,
    branch_from: str,
    branch_to: str,
    pr_url: str,
    repo: str,
    labels: str = "-",
    milestone: str = None,
    merged: bool = False  # 👈 nuevo
):
    card_title = "✅ Pull Request *mergeado*" if merged else "🧪 Nuevo Pull Request"
    card_summary = f"{card_title} en {repo}"

    # Armar bloques de etiquetas (ahora sólo acá se formatean con backticks)
    if labels != "-" and labels.strip():
        label_names = [l.strip() for l in labels.split(",")]
        label_blocks = " ".join(f"`{l}`" for l in label_names)
    else:
        label_blocks = "(ninguna)"

    # Construcción base de facts
    facts = [
        {"name": "📄 Título", "value": title},
        {"name": "🔢 Número", "value": f"#{pr_number}"},
        {"name": "👤 Autor", "value": sender},
        {"name": "🌿 Ramas", "value": f"`{branch_from}` → `{branch_to}`"},
        {"name": "🏷️ Labels", "value": label_blocks},
    ]

    # Si hay milestone, agregarlo
    if milestone:
        facts.append({"name": "📌 Milestone", "value": milestone})

    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": card_summary,
        "themeColor": "0076D7",
        "sections": [
            {
                "activityTitle": f"{card_title} en `{repo}`",
                "facts": facts,
                "markdown": True
            }
        ],
        "potentialAction": [
            {
                "@type": "OpenUri",
                "name": "Ver Pull Request",
                "targets": [{"os": "default", "uri": pr_url}]
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=card)
            print(f"[Teams] Status: {response.status_code}")
            print(f"[Teams] Body: {response.text}")
            return response.status_code, response.text
    except Exception as e:
        print(f"[Teams] ERROR: {e}")
        raise e
