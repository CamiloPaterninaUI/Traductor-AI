# main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse  # ← una sola importación
from pydantic import BaseModel
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import httpx
import json

# Semilla fija para resultados consistentes
DetectorFactory.seed = 42

# ---------------------------------------------------------------------------
# Configuración de la app
# ---------------------------------------------------------------------------

app = FastAPI(title="Traductor IA - Ollama + Qwen")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5:3b"

# FIX: límite de caracteres consistente con el frontend
MAX_TEXT_LENGTH = 5000

# ---------------------------------------------------------------------------
# Idiomas soportados
# ---------------------------------------------------------------------------

LANGUAGES: dict[str, str] = {
    "es": "Español",
    "en": "English",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "it": "Italiano",
    "zh-cn": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "ru": "Русский",
    "ar": "العربية",
    "nl": "Nederlands",
}

# Nombres completos en inglés para el prompt del LLM
LANG_NAMES_EN: dict[str, str] = {
    "es": "Spanish",
    "en": "English",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "it": "Italian",
    "zh-cn": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "ar": "Arabic",
    "nl": "Dutch",
}

# ---------------------------------------------------------------------------
# Modelos de datos
# ---------------------------------------------------------------------------

class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "en"

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    """Detecta el idioma del texto con langdetect. Devuelve código ISO."""
    try:
        detected = detect(text)
        # Normalizar zh-cn / zh-tw → zh-cn
        if detected.startswith("zh"):
            return "zh-cn"
        # Verificar que el idioma detectado está en nuestra lista
        return detected if detected in LANG_NAMES_EN else "en"
    except LangDetectException:
        return "en"


def build_prompt(text: str, source_lang: str, target_lang: str) -> str:
    """Construye el prompt de traducción para el LLM."""
    src_name = LANG_NAMES_EN.get(source_lang, source_lang)
    tgt_name = LANG_NAMES_EN.get(target_lang, target_lang)

    return f"""You are an expert professional translator specializing in accurate, natural-sounding translations.

Translate the following {src_name} text into {tgt_name}.

Rules:
- Return ONLY the translated text. No explanations, no notes, no quotes.
- Preserve all formatting, line breaks, and punctuation exactly.
- Maintain the tone and register of the original (formal/informal).
- Keep proper nouns, brand names, and technical terms unless a standard translation exists.

Text:
{text}

Translation:"""

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Verifica que Ollama esté corriendo y lista los modelos disponibles."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            res = await client.get(f"{OLLAMA_URL}/api/tags")
            res.raise_for_status()
            models = [m["name"] for m in res.json().get("models", [])]
            return {"status": "ok", "model": MODEL, "ollama_models": models}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama no disponible: {e}")


@app.get("/languages")
def get_languages() -> dict[str, str]:
    """Retorna el diccionario de idiomas soportados."""
    return LANGUAGES


@app.post("/translate")
async def translate(req: TranslateRequest):
    """Traduce el texto usando Ollama con streaming SSE."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")

    # FIX: validar longitud máxima en el backend
    if len(req.text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"El texto excede el límite de {MAX_TEXT_LENGTH} caracteres."
        )

    # FIX: validar idioma destino
    if req.target_lang not in LANG_NAMES_EN:
        raise HTTPException(
            status_code=400,
            detail=f"Idioma destino no soportado: {req.target_lang}"
        )

    # FIX: validar idioma fuente cuando no es "auto"
    if req.source_lang != "auto" and req.source_lang not in LANG_NAMES_EN:
        raise HTTPException(
            status_code=400,
            detail=f"Idioma fuente no soportado: {req.source_lang}"
        )

    # Detectar idioma si viene como "auto"
    actual_source = (
        detect_language(req.text) if req.source_lang == "auto" else req.source_lang
    )

    # Si origen y destino son el mismo, devolver el texto tal cual
    if actual_source == req.target_lang:
        async def same_lang_stream():
            yield f"data: {json.dumps({'detected_lang': actual_source})}\n\n"
            yield f"data: {json.dumps({'token': req.text})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(same_lang_stream(), media_type="text/event-stream")

    prompt = build_prompt(req.text, actual_source, req.target_lang)

    async def translation_stream():
        # Emitir primero el idioma detectado
        yield f"data: {json.dumps({'detected_lang': actual_source})}\n\n"

        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1,
                    },
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield f"data: {json.dumps({'token': token})}\n\n"
                        if data.get("done"):
                            yield "data: [DONE]\n\n"
                    except json.JSONDecodeError:
                        continue

    return StreamingResponse(translation_stream(), media_type="text/event-stream")


@app.get("/")
def serve_frontend():
    return FileResponse("index.html")
