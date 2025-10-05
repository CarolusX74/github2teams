# 🧩 GitHub2Teams

**GitHub2Teams** es un servicio ligero y autogestionado que escucha _webhooks_ de **GitHub** y envía notificaciones formateadas a canales de **Microsoft Teams**.

Permite manejar múltiples repositorios y canales desde un panel web seguro, con autenticación por sesión y configuración persistente.

---

## 🚀 Características

- Soporte completo para **eventos de Pull Requests** (`opened`, `reopened`, `closed` / `merged`).
- Detección automática de **merges** desde eventos `push`.
- Envío de tarjetas enriquecidas a **Microsoft Teams** con información de PR, etiquetas y milestone.
- Panel web protegido con **login y sesión segura**.
- Configuración persistente en `data/config.json`.
- Compatible con Docker y listo para producción.

---

## 🐳 Despliegue con Docker Compose

Crea un archivo `docker-compose.yml` como este:

```yaml
version: '3.9'

services:
  github2teams:
    image: carolusx74/github2teams:latest
    container_name: github2teams
    restart: always
    ports:
      - "8011:8000"
    volumes:
      - ./data:/app/data
    environment:
      # 🔐 Clave usada para validar firmas HMAC de GitHub
      - WEBHOOK_SECRET=my-webhook-secret

      # 👤 Credenciales del panel de administración
      - ADMIN_USER=admin
      - ADMIN_PASS=superseguro123

      # 🔑 Secreto de sesión para cookies seguras
      - SESSION_SECRET=c61b4c13c2bf401e03f1c4870677b81b39eff7a0db46972d966cfe4adc743d76

    networks:
      - github2teams-net

networks:
  github2teams-net:
    driver: bridge
```

Luego ejecuta:

```bash
docker-compose up -d
```

El panel estará disponible en:

👉 **http://localhost:8011/admin**

---

## ⚙️ Configuración de GitHub

1. En tu repositorio de GitHub, ve a  
   **Settings → Webhooks → Add webhook**.

2. En **Payload URL**, ingresa la URL pública del endpoint:  
   ```
   https://tuservidor.com/github
   ```

3. En **Content type**, selecciona  
   `application/json`.

4. En **Secret**, ingresa el mismo valor definido en  
   `WEBHOOK_SECRET` del `docker-compose.yml`.

5. Marca solo los eventos:
   - ✅ Pull requests
   - ✅ Pushes

6. Guarda el webhook y prueba el envío desde GitHub.

---

## 🧠 Panel de administración

Desde el panel `/admin` puedes:

- Agregar o eliminar repositorios.
- Registrar múltiples URLs de Teams por repositorio.
- Configurar o actualizar la clave HMAC.
- Enviar mensajes de prueba.
- Cerrar sesión segura.

---

## 💡 Ejemplo de uso

- **Repositorio:** `empresa/proyecto`
- **Webhook de Teams:**  
  `https://outlook.office.com/webhook/...`

Cuando se abra un nuevo Pull Request o se haga merge, el canal de Teams recibirá una tarjeta similar a:

> 🟩 **New Pull Request #42**  
> _feature/login → main_  
> Autor: @carlospensa  
> Labels: ALTAS, CORE  
> Milestone: v1.2.0  

---

## 🔐 Seguridad

- El panel requiere autenticación (`ADMIN_USER` / `ADMIN_PASS`).
- Cada sesión usa un `SESSION_SECRET` único.
- Los webhooks se validan mediante **HMAC-SHA256**.
- Configuración sensible persistida localmente (`data/config.json`).

---

## ☕ Apoyar el proyecto

Si este proyecto te resulta útil, podés invitarme un café o contribuir a su mantenimiento 💙  

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/carolusx74)  
[Buy me a coffee ☕](https://www.buymeacoffee.com/carolusx74)

---

## 📜 Licencia

Distribuido bajo la **MIT License**.  
Consulta el archivo [LICENSE](./LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Carlos Javier Torres Pensa**  
Desarrollador Android & DevOps — Argentina 🇦🇷  
📧 [carlosjtp.777@gmail.com](mailto:carlosjtp.777@gmail.com)  
🌐 [https://pensa.com.ar](https://pensa.com.ar)

© 2025 Carlos Javier Torres Pensa — _All rights reserved_.
