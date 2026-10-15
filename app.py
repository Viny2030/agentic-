import os
import sys
import json
import time
import base64
import mimetypes
import importlib
from datetime import datetime
import numpy as np
import anthropic
import gradio as gr
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# ==============================================================================
# 1. CONFIGURACIÓN Y CLIENTE ANTHROPIC (MULTIMODAL LOW-COST)
# ==============================================================================
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=API_KEY) if API_KEY else None

# Modelos recomendados con soporte multimodal (visión de imágenes y documentos)
MODELO_BASE = "claude-3-5-sonnet-20241022"
MODELO_FALLBACK = "claude-3-haiku-20240307"


# ==============================================================================
# 2. LAS 5 HERRAMIENTAS AVANZADAS DE CONTROL
# ==============================================================================

# --- A. OMNI ROUTE ---
def tool_omni_route(tarea: str, complejidad: str = "auto") -> str:
    """Enruta subtareas al ejecutor o modelo más eficiente."""
    t = tarea.lower()
    if any(k in t for k in ["cuant", "qubit", "bell", "qiskit", "ionq", "entrelazamiento"]):
        subagente = "subagente_cuantico"
        modelo = MODELO_BASE
    elif any(k in t for k in ["estadíst", "media", "std", "datos", "numpy", "pandas"]):
        subagente = "subagente_clasico"
        modelo = MODELO_BASE
    elif any(k in t for k in ["imagen", "diagrama", "foto", "grafico", "ocr", "documento"]):
        subagente = "subagente_vision_multimodal"
        modelo = MODELO_BASE
    elif any(k in t for k in ["teoria", "explica", "arquitectura"]):
        subagente = "analizador_profundo"
        modelo = "claude-3-7-sonnet-20250219" if complejidad in ["alta", "auto"] else MODELO_BASE
    else:
        subagente = "ejecutor_general"
        modelo = MODELO_BASE

    return json.dumps({
        "status": "enrutado",
        "subagente": subagente,
        "modelo_sugerido": modelo
    }, ensure_ascii=False)


# --- B. CLAUDE MEM ---
MEMORIA_FILE = "memoria_agente.json"


def _cargar_memoria():
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _guardar_memoria(data):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def tool_claude_mem(accion: str, clave: str, valor: str = "") -> str:
    """Memoria persistente en disco (JSON)."""
    mem = _cargar_memoria()
    if accion == "guardar":
        if not valor:
            return json.dumps({"error": "Falta el valor para guardar."})
        mem[clave] = {"valor": valor, "actualizado": datetime.now().isoformat()}
        _guardar_memoria(mem)
        return json.dumps({"status": "guardado", "clave": clave})
    elif accion == "leer":
        if clave in mem:
            return json.dumps({"clave": clave, "registro": mem[clave]}, ensure_ascii=False)
        return json.dumps({"status": "no_encontrado", "clave": clave})
    elif accion == "listar":
        return json.dumps({"claves": list(mem.keys())})
    elif accion == "borrar":
        if clave in mem:
            del mem[clave]
            _guardar_memoria(mem)
            return json.dumps({"status": "borrado", "clave": clave})
        return json.dumps({"status": "inexistente", "clave": clave})
    return json.dumps({"error": f"Accion {accion} invalida"})


# --- C. HEADROOM ---
def tool_headroom(turnos_historial: int, tokens_estimados: int = 0) -> str:
    """Calcula el margen libre de tokens en la ventana de contexto."""
    LIMITE = 200000
    consumo = tokens_estimados if tokens_estimados > 0 else (turnos_historial * 250)
    disponible = max(0, LIMITE - consumo)
    alerta = "OPTIMO" if disponible > 80000 else ("MODERADO" if disponible > 30000 else "CRITICO_PODAR")
    return json.dumps({
        "consumo_aprox": consumo,
        "headroom_disponible": disponible,
        "alerta": alerta
    })


# --- D. CLAUDE CODE SETUP ---
def tool_claude_code_setup(accion: str = "verificar_todo") -> str:
    """Verifica dependencias del entorno, claves y sistema."""
    libs = ["anthropic", "qiskit", "qiskit_aer", "numpy", "gradio", "PIL"]
    res_libs = {}
    for lib in libs:
        try:
            m = importlib.import_module(lib)
            res_libs[lib] = {"disponible": True, "version": getattr(m, "__version__", "ok")}
        except ImportError:
            res_libs[lib] = {"disponible": False, "version": None}

    claves = ["ANTHROPIC_API_KEY", "IONQ_API_KEY", "IBM_QUANTUM_TOKEN"]
    res_claves = {c: ("Configurada" if os.environ.get(c) else "Faltante") for c in claves}

    return json.dumps({
        "python": sys.version.split()[0],
        "librerias": res_libs,
        "claves": res_claves
    }, indent=2)


# --- E. TASK OBSERVER ---
_LOGS_SESION = []


def tool_task_observer(id_tarea: str, estado: str, detalle: str) -> str:
    """Registra y audita el progreso de cada subtarea; detecta bucles repetitivos."""
    global _LOGS_SESION
    registro = {"t": time.time(), "id": id_tarea, "estado": estado, "detalle": detalle}
    _LOGS_SESION.append(registro)
    print(f"👁️ [OBSERVER] [{estado.upper()}] ({id_tarea}): {detalle}")

    ultimos = [r["detalle"] for r in _LOGS_SESION[-3:]]
    es_bucle = len(ultimos) == 3 and len(set(ultimos)) == 1

    return json.dumps({
        "status": "registrado",
        "tarea": id_tarea,
        "estado": estado,
        "alerta_bucle": es_bucle
    })


# ==============================================================================
# 3. HERRAMIENTAS DE CÓMPUTO CIENTÍFICO (DATOS + CUÁNTICO)
# ==============================================================================

def tool_analisis_clasico(datos: list[float]) -> str:
    """Calcula media, std, min y max de una serie numérica."""
    arr = np.array(datos)
    return json.dumps({
        "media": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "n": len(arr)
    })


def tool_circuito_bell() -> str:
    """Ejecuta una simulación de entrelazamiento cuántico con Qiskit Aer."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    sim = AerSimulator()
    job = sim.run(qc, shots=1000)
    return json.dumps({
        "shots": 1000,
        "conteo": job.result().get_counts(),
        "estado": "Entrelazamiento Bell Phi+"
    })


herramientas_map = {
    "tool_omni_route": tool_omni_route,
    "tool_claude_mem": tool_claude_mem,
    "tool_headroom": tool_headroom,
    "tool_claude_code_setup": tool_claude_code_setup,
    "tool_task_observer": tool_task_observer,
    "tool_analisis_clasico": tool_analisis_clasico,
    "tool_circuito_bell": tool_circuito_bell
}

# ==============================================================================
# 4. ESQUEMA FORMAL DE HERRAMIENTAS
# ==============================================================================
tools_schema = [
    {
        "name": "tool_omni_route",
        "description": "Enruta la subtarea al componente o modelo más óptimo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tarea": {"type": "string"},
                "complejidad": {"type": "string", "enum": ["baja", "media", "alta", "auto"]}
            },
            "required": ["tarea"]
        }
    },
    {
        "name": "tool_claude_mem",
        "description": "Memoria persistente: almacena o consulta información entre sesiones.",
        "input_schema": {
            "type": "object",
            "properties": {
                "accion": {"type": "string", "enum": ["guardar", "leer", "listar", "borrar"]},
                "clave": {"type": "string"},
                "valor": {"type": "string"}
            },
            "required": ["accion", "clave"]
        }
    },
    {
        "name": "tool_headroom",
        "description": "Verifica margen de tokens libres en la ventana de contexto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "turnos_historial": {"type": "integer"},
                "tokens_estimados": {"type": "integer"}
            },
            "required": ["turnos_historial"]
        }
    },
    {
        "name": "tool_claude_code_setup",
        "description": "Audita entorno de ejecución, librerías y API keys.",
        "input_schema": {
            "type": "object",
            "properties": {
                "accion": {"type": "string", "enum": ["verificar_todo", "verificar_librerias", "verificar_claves"]}
            }
        }
    },
    {
        "name": "tool_task_observer",
        "description": "Registra pasos de tareas y detecta bucles repetitivos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id_tarea": {"type": "string"},
                "estado": {"type": "string", "enum": ["iniciado", "en_progreso", "completado", "fallido"]},
                "detalle": {"type": "string"}
            },
            "required": ["id_tarea", "estado", "detalle"]
        }
    },
    {
        "name": "tool_analisis_clasico",
        "description": "Calcula estadísticas descriptivas sobre una lista numérica.",
        "input_schema": {
            "type": "object",
            "properties": {
                "datos": {"type": "array", "items": {"type": "number"}}
            },
            "required": ["datos"]
        }
    },
    {
        "name": "tool_circuito_bell",
        "description": "Simula un circuito cuántico de Bell con Qiskit Aer.",
        "input_schema": {"type": "object", "properties": {}}
    }
]


# ==============================================================================
# 5. PROCESAMIENTO MULTIMODAL (IMÁGENES Y ARCHIVOS)
# ==============================================================================
def procesar_archivo_adjunto(file_path: str):
    """
    Convierte una imagen o documento adjunto al formato aceptado por la API de Claude.
    Soporta imágenes (PNG, JPEG, GIF, WEBP), PDFs nativos y archivos de texto/código/CSV.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    nombre_archivo = os.path.basename(file_path)

    # 1. Si es Imagen soportada por la API de Anthropic
    if mime_type in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        with open(file_path, "rb") as f:
            data_b64 = base64.b64encode(f.read()).decode("utf-8")
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime_type,
                "data": data_b64
            }
        }

    # 2. Si es Documento PDF nativo
    elif mime_type == "application/pdf":
        with open(file_path, "rb") as f:
            data_b64 = base64.b64encode(f.read()).decode("utf-8")
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": data_b64
            }
        }

    # 3. Si es archivo de texto, código, csv, json, md, etc.
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                contenido_txt = f.read()
            return {
                "type": "text",
                "text": f"--- ARCHIVO ADJUNTO: {nombre_archivo} ---\n{contenido_txt}\n--- FIN DE ARCHIVO ---"
            }
        except Exception as e:
            return {
                "type": "text",
                "text": f"[No se pudo leer el archivo {nombre_archivo}: {str(e)}]"
            }


def invocar_claude_seguro(mensajes, sistema):
    """Ejecuta la llamada a Claude con fallback de modelo."""
    global client
    for mod in [MODELO_BASE, MODELO_FALLBACK]:
        try:
            return client.messages.create(
                model=mod,
                max_tokens=1500,
                system=sistema,
                tools=tools_schema,
                messages=mensajes
            )
        except anthropic.NotFoundError:
            continue
    return client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1500,
        system=sistema,
        tools=tools_schema,
        messages=mensajes
    )


# ==============================================================================
# 6. BUCLE AGÉNTICO MULTIMODAL CON GRADIO
# ==============================================================================
def responder_chat(mensaje, historial):
    global client

    activa = API_KEY or os.environ.get("ANTHROPIC_API_KEY")
    if not activa:
        return "⚠️ Error: Falta la variable ANTHROPIC_API_KEY. Configurala en tu entorno."

    if not client:
        client = anthropic.Anthropic(api_key=activa)

    # En Gradio con multimodal=True, 'mensaje' es un dict: {"text": "...", "files": ["ruta1", ...]}
    texto_usuario = ""
    archivos_adjuntos = []

    if isinstance(mensaje, dict):
        texto_usuario = mensaje.get("text", "") or ""
        archivos_adjuntos = mensaje.get("files", []) or []
    else:
        texto_usuario = str(mensaje)

    # Construir contenido del mensaje de Claude (bloques mixtos de texto, imágenes y archivos)
    bloques_contenido = []

    # Procesar archivos e imágenes adjuntos
    for ruta in archivos_adjuntos:
        bloque = procesar_archivo_adjunto(ruta)
        bloques_contenido.append(bloque)

    # Agregar el texto o prompt del usuario
    if texto_usuario.strip():
        bloques_contenido.append({"type": "text", "text": texto_usuario})
    elif archivos_adjuntos:
        bloques_contenido.append({"type": "text", "text": "Analizá y describí en detalle la imagen o archivo adjunto."})
    else:
        bloques_contenido.append({"type": "text", "text": "Hola."})

    mensajes = [{"role": "user", "content": bloques_contenido}]

    prompt_sistema = (
        "Sos un asistente científico y de ingeniería agéntica con capacidades de cómputo cuántico, "
        "análisis de datos y visión artificial multimodal. "
        "Podés inspeccionar diagramas, circuitos, fotos, documentos PDF y datos crudos. "
        "Disponés de herramientas de control (omni_route, claude_mem, headroom, code_setup, task_observer) "
        "y de cómputo (tool_analisis_clasico, tool_circuito_bell). Respondé siempre en español de forma precisa y concisa."
    )

    try:
        max_pasos = 6
        for _ in range(max_pasos):
            res = invocar_claude_seguro(mensajes, prompt_sistema)

            if res.stop_reason != "tool_use":
                for bloque in res.content:
                    if hasattr(bloque, "text"):
                        return bloque.text
                return "Ejecución finalizada."

            mensajes.append({"role": "assistant", "content": res.content})
            resultados_herramientas = []

            for bloque in res.content:
                if bloque.type == "tool_use":
                    nombre_fn = bloque.name
                    args = bloque.input

                    if nombre_fn in herramientas_map:
                        salida = herramientas_map[nombre_fn](**args)
                    else:
                        salida = json.dumps({"error": f"Herramienta {nombre_fn} no encontrada"})

                    resultados_herramientas.append({
                        "type": "tool_result",
                        "tool_use_id": bloque.id,
                        "content": salida
                    })

            mensajes.append({"role": "user", "content": resultados_herramientas})

        return "Se completaron los pasos disponibles."

    except Exception as e:
        return f"🚨 Error de ejecución: {type(e).__name__} - {str(e)}"


# ==============================================================================
# 7. INTERFAZ WEB GRADIO MULTIMODAL
# ==============================================================================
demo = gr.ChatInterface(
    fn=responder_chat,
    title="⚛️ Asistente Agéntico Multimodal: Cómputo Cuántico, Datos y Visión",
    description="Subí imágenes, diagramas de circuitos, PDFs o datos crudos junto con tus preguntas. Suite completa de herramientas activas.",
    multimodal=True
)

if __name__ == "__main__":
    demo.launch()
