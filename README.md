# 🎮 AutomataLol - Premium League of Legends Lobby Automation

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-stable-success)

**Automatización profesional de lobby para League of Legends**

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso) • [Documentación](#-documentación) • [Contribuciones](#-contribuciones)

</div>

---

## 🚀 Características

### ✅ **Automatización Completa**
- **Auto Accept** - Aceptación automática de queue con delays humanizados
- **Auto Ban** - Baneo inteligente con prioridades múltiples
- **Auto Pick** - Selección automática con fallback y safe mode
- **Auto Runes** - Importación automática (OP.GG, U.GG, Porofessor, Mobalytics)
- **Auto Summoner Spells** - Asignación automática por rol
- **Smart Detection** - Detección inteligente de fases (LCU + OCR + Vision)

### 🏛️ **Arquitectura Enterprise**
- ✅ Modular y escalable
- ✅ Event Bus centralizado
- ✅ Async/await 100% non-blocking
- ✅ Tipado completo (Python 3.12+)
- ✅ Manejo robusto de errores
- ✅ Logging integrado
- ✅ Configuración persistente

### 🔐 **Seguridad**
- ✅ No modifica memoria
- ✅ No usa drivers kernel
- ✅ No inyecta DLLs
- ✅ No tiene bypasses
- ✅ Solo usa LCU API oficial
- ✅ Compatible con anti-cheat

### ⚙️ **Rendimiento**
- ✅ Bajo consumo de RAM
- ✅ Uso mínimo de CPU
- ✅ Threading optimizado
- ✅ Reconexión automática

---

## 📋 Requisitos

- **Sistema Operativo**: Windows 10/11
- **Python**: 3.12 o superior
- **League of Legends**: Cliente LCU actualizado
- **RAM**: 256 MB mínimo
- **Conexión**: Conexión estable a internet

---

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/NiiKo23/AutomataLol.git
cd AutomataLol
```

### 2. Crear entorno virtual

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python main.py
```

---

## 🎯 Uso Rápido

### Ejecutar con configuración por defecto

```bash
python main.py
```

**Salida esperada:**
```
============================================================
🚀 AutomataLol Starting...
============================================================
Loading configuration...
✅ Configuration loaded
Connecting to League Client...
✅ LCU Client connected
Enabling automations...
✅ Automations enabled
============================================================
✅ AutomataLol ready!
============================================================
```

### Configuración básica

Editar `~/.automatalol/config.json`:

```json
{
  "auto_accept": {
    "enabled": true,
    "delay_ms": 50,
    "humanize_delay": true
  },
  "auto_ban": {
    "enabled": true,
    "primary_bans": ["Yasuo", "Zed", "Ahri"],
    "secondary_bans": ["Sylas"]
  },
  "auto_pick": {
    "enabled": true,
    "champion": "Ahri",
    "fallback_picks": ["Annie", "Lux"],
    "safe_mode": true
  },
  "auto_runes": {
    "enabled": true,
    "auto_import": true,
    "preferred_source": "opgg"
  }
}
```

---

## 📚 Uso Avanzado

### Uso Programático

```python
import asyncio
from services import lcu_service
from modules import auto_accept, auto_ban, auto_pick

async def main():
    # Conectar a LCU
    if not await lcu_service.start():
        print("Error: No se pudo conectar a LCU")
        return
    
    # Configurar automaciones
    auto_ban.set_bans(
        primary=["Yasuo", "Zed"],
        secondary=["Ahri"]
    )
    auto_pick.set_champion("Ahri")
    auto_pick.set_fallbacks(["Annie", "Lux"])
    
    # Habilitar
    await auto_accept.enable()
    await auto_ban.enable()
    await auto_pick.enable()
    
    # Mantener corriendo
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo...")
        await lcu_service.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Event Bus

```python
from core.events import get_event_bus, EventType

event_bus = get_event_bus()

# Suscribirse a eventos
event_bus.subscribe(
    EventType.QUEUE_FOUND,
    lambda event: print("Queue encontrada!"),
    priority=10
)

event_bus.subscribe(
    EventType.AUTO_ACCEPT_EXECUTED,
    lambda event: print("Queue aceptada!"),
    priority=10
)

# Ver historial de eventos
history = event_bus.get_history(limit=50)
for event in history:
    print(f"{event.timestamp} - {event.type}: {event.data}")

# Estadísticas
stats = event_bus.get_statistics()
print(f"Total eventos: {stats['total_events']}")
```

---

## 🏗️ Arquitectura

```
AutoмataLol/
├── core/                          # Sistema principal
│   ├── constants.py              # Constantes globales
│   ├── exceptions.py             # Excepciones tipadas
│   ├── events.py                 # Event Bus centralizado
│   └── __init__.py
│
├── api/                          # Cliente LCU
│   ├── client.py                 # Cliente HTTP + SSL
│   ├── events.py                 # WebSocket listener
│   └── __init__.py
│
├── modules/                      # Automatizaciones
│   ├── auto_accept.py           # Auto Accept
│   ├── auto_ban.py              # Auto Ban
│   ├── auto_pick.py             # Auto Pick
│   ├── auto_runes.py            # Auto Runes
│   ├── auto_summoner.py         # Auto Summoner
│   ├── lobby_detector.py        # Smart Detection
│   └── __init__.py
│
├── services/                     # Servicios
│   ├── lcu_service.py           # Orquestador LCU
│   ├── config_service.py        # Configuración
│   └── __init__.py
│
├── utils/                        # Utilidades
│   ├── logger.py                # Logging
│   ├── helpers.py               # Funciones auxiliares
│   └── __init__.py
│
├── main.py                       # Entry point
├── requirements.txt              # Dependencias
└── README.md                     # Este archivo
```

---

## 🔌 LCU API

AutoмataLol utiliza la **League Client Update (LCU) API** oficial:

```python
from api import get_lcu_client

client = get_lcu_client()
await client.connect()

# GET - Obtener datos
summoner = await client.get("/lol-summoner/v1/current-summoner")
session = await client.get("/lol-champ-select/v1/session")

# POST - Aceptar queue
await client.post("/lol-matchmaking/v1/ready-check/accept", data={})

# PATCH - Cambiar pick
await client.patch(
    f"/lol-champ-select/v1/session/actions/{action_id}",
    data={"championId": 1, "completed": True}
)
```

### Endpoints soportados

- `GET /lol-summoner/v1/current-summoner` - Obtener invocador actual
- `GET /lol-champ-select/v1/session` - Obtener sesión de selección
- `GET /lol-matchmaking/v1/search` - Obtener búsqueda de partida
- `POST /lol-matchmaking/v1/ready-check/accept` - Aceptar queue
- `POST /lol-matchmaking/v1/ready-check/decline` - Rechazar queue
- `PATCH /lol-champ-select/v1/session/actions/{id}` - Ejecutar acción

---

## 📊 Event Types

```python
from core.events import EventType

EventType.QUEUE_FOUND                    # Queue encontrada
EventType.READY_CHECK_FOUND              # Ready check
EventType.READY_CHECK_ACCEPTED           # Ready check aceptado
EventType.READY_CHECK_DECLINED           # Ready check rechazado
EventType.CHAMP_SELECT_START             # Selección de campeón
EventType.BAN_PHASE_START                # Fase de baneo
EventType.BAN_PHASE_END                  # Fin de fase de baneo
EventType.PICK_PHASE_START               # Fase de selección
EventType.PICK_PHASE_END                 # Fin de fase de selección
EventType.AUTO_ACCEPT_EXECUTED           # Auto Accept ejecutado
EventType.AUTO_BAN_EXECUTED              # Auto Ban ejecutado
EventType.AUTO_PICK_EXECUTED             # Auto Pick ejecutado
EventType.AUTO_RUNES_EXECUTED            # Auto Runes ejecutado
EventType.AUTOMATION_FAILED              # Automatización falló
EventType.LCU_SERVICE_READY              # Servicio LCU listo
```

---

## 🛠️ Desarrollo

### Estructura de código

```python
# 1. Importar eventos
from core.events import get_event_bus, EventType

# 2. Crear clase
class MyModule:
    def __init__(self):
        self.event_bus = get_event_bus()
    
    async def run(self):
        # 3. Emitir evento
        await self.event_bus.emit_async(
            EventType.CUSTOM_EVENT,
            data={"key": "value"},
            source="MyModule"
        )

# 4. Suscribirse
event_bus = get_event_bus()
event_bus.subscribe(
    EventType.CUSTOM_EVENT,
    lambda event: print(event.data)
)
```

### Crear nuevo módulo

```python
# modules/my_module.py
import asyncio
from core.events import get_event_bus, EventType

class MyAutomation:
    def __init__(self):
        self.event_bus = get_event_bus()
        self.enabled = False
    
    async def enable(self):
        self.enabled = True
        self.event_bus.subscribe(
            EventType.TRIGGER_EVENT,
            lambda e: asyncio.create_task(self.run(e)),
            async_handler=True
        )
    
    async def run(self, event):
        print("Ejecutando automatización...")
        # Lógica aquí
        await self.event_bus.emit_async(
            EventType.AUTOMATION_EXECUTED,
            data={"status": "success"},
            source="MyAutomation"
        )
```

---

## 🐛 Solución de Problemas

### No se conecta a LCU

1. Asegúrate de que **League of Legends esté abierto**
2. Verifica que el **cliente esté actualizado**
3. Comprueba los **logs** en `~/.automatalol/logs/`

```bash
# Ver logs
tail -f ~/.automatalol/logs/AutomataLol.log
```

### Auto Accept no funciona

1. Verifica que esté **habilitado** en config
2. Comprueba que **no haya dodge activo**
3. Mira los **logs de eventos**

### Error de permiso SSL

1. Intenta ejecutar como **administrador**
2. Reinicia el **cliente de LoL**
3. Limpia la **carpeta de certificados**: `~/.automatalol/`

---

## 📝 Configuración Avanzada

### Delays humanizados

```python
from utils import humanize_delay

# Base 50ms ± 30ms varianza
delay = humanize_delay(50, 30)
await asyncio.sleep(delay)
```

### Reintentos automáticos

```python
from utils import retry_async

@retry_async(max_retries=3, delay=1.0)
async def risky_operation():
    # Reintentará hasta 3 veces si falla
    pass
```

### Logging personalizado

```python
from utils import get_logger

logger = get_logger(__name__)
logger.info("Información")
logger.warning("Advertencia")
logger.error("Error", exc_info=True)
```

---

## 📊 Performance

| Métrica | Valor |
|---------|-------|
| **RAM** | ~50-100 MB |
| **CPU** | <1% (idle) |
| **Latencia** | <100ms |
| **Conexión** | SSL/TLS |
| **Reintentos** | Exponential backoff |

---

## 🔒 Seguridad

### ✅ No hace
- ❌ No modifica memoria
- ❌ No usa drivers kernel
- ❌ No inyecta DLLs
- ❌ No tiene bypasses
- ❌ No interactúa durante la partida

### ✅ Solo usa
- ✅ LCU API oficial
- ✅ Comunicación segura SSL/TLS
- ✅ Eventos públicos del cliente
- ✅ Automatización de interfaz

---

## 📄 Licencia

MIT License - Ver `LICENSE` para detalles

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📞 Soporte

- **Issues**: Abre un issue en GitHub
- **Documentación**: Lee el README
- **Logs**: Revisa `~/.automatalol/logs/`

---

## ⚠️ Disclaimer

AutoмataLol es una herramienta para automatización de lobby. El uso no está garantizado que cumpla con los Términos de Servicio de Riot Games. Úsalo bajo tu propio riesgo.

---

<div align="center">

**Hecho con ❤️ para la comunidad de League of Legends**

![AutomataLol](https://img.shields.io/badge/AutomataLol-1.0.0-blue?style=for-the-badge)

</div>
