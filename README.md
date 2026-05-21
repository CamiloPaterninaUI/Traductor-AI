cat > README.md << 'EOF'
# 🌐 Traductor-AI

Traductor web con inteligencia artificial que corre **100% local** usando [Ollama](https://ollama.com) + **Qwen 2.5 3B**. Detecta el idioma automáticamente y traduce en tiempo real con streaming token a token.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi) ![Ollama](https://img.shields.io/badge/Ollama-local-black?logo=ollama) ![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Características

- Detección automática del idioma con `langdetect`
- Traducción en streaming (respuesta token a token)
- 12 idiomas soportados: Español, English, Français, Deutsch, Português, Italiano, 中文, 日本語, 한국어, Русский, العربية, Nederlands
- Interfaz glassmorphism moderna, sin dependencias frontend (HTML puro)
- 100% local — ningún dato sale de tu máquina
- Botón intercambiar idiomas inteligente (funciona incluso con detección automática)

---

## 🗂 Estructura del proyecto

\`\`\`
Traductor-AI/
├── main.py            # Backend FastAPI con streaming SSE
├── index.html         # Frontend (servido por FastAPI)
├── requirements.txt   # Dependencias Python
└── README.md
\`\`\`

---

## ⚙️ Requisitos previos

- Python 3.10 o superior
- [Ollama](https://ollama.com/download) instalado y corriendo
- El modelo \`qwen2.5:3b\` descargado en Ollama

---

## 🚀 Instalación y uso

### 1. Clona el repositorio

\`\`\`bash
git clone https://github.com/CamiloPaterninaUI/Traductor-AI.git
cd Traductor-AI
\`\`\`

### 2. Instala las dependencias Python

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Descarga el modelo en Ollama

\`\`\`bash
ollama pull qwen2.5:3b
\`\`\`

### 4. Inicia Ollama

\`\`\`bash
ollama serve
\`\`\`

### 5. Inicia el backend

\`\`\`bash
uvicorn main:app --reload --port 8000
\`\`\`

### 6. Abre el traductor

Visita **http://localhost:8000** en tu navegador.

---

## 🖥 Uso

| Acción | Cómo |
|--------|------|
| Traducir | Escribe el texto y presiona **Traducir** |
| Atajo de teclado | Ctrl + Enter · ⌘ + Enter (Mac) |
| Detección automática | Deja seleccionado **Detectar** en el panel izquierdo |
| Intercambiar idiomas | Click en el botón ⇅ del centro |
| Copiar traducción | Aparece el botón **Copiar** al terminar |

---

## 🔌 API endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | / | Sirve el frontend |
| GET | /health | Estado de Ollama y modelo activo |
| GET | /languages | Lista de idiomas soportados |
| POST | /translate | Traduce con streaming SSE |

---

## 📄 Licencia

MIT — libre para usar, modificar y distribuir.
EOF
