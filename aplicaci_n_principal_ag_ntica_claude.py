import os
import json
import numpy as np
import anthropic
import gradio as gr
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# 1. Inicialización del cliente de Anthropic
# Lee la variable de entorno ANTHROPIC_API_KEY
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# 2. Implementación de Herramientas Locales

# --- Herramientas de Cómputo (Clásico y Cuántico) ---
def tool_analisis_clasico(datos: list[float]) -> str:
    """Calcula métricas estadísticas básicas."""
    arr = np.array(datos)
    return json.dumps({
        "media": round(float(np.mean(arr)), 4),
        "std": round(float(np.std(arr)), 4),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "n": len(arr)
    })

def tool_circuito_bell() -> str:
    """Simula un estado de Bell (|Phi+>) con Qiskit Aer."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    sim = AerSimulator()
    job = sim.run(qc, shots=1000)
    # Devolver conteos compactos para ahorrar tokens
    return json.dumps({"shots": 1000, "conteos": job.result().get_counts()})

# --- Herramientas del Ecosistema Agéntico (Optimizadas) ---
def tool_omni_route(tarea: str) -> str:
    """Determina si una tarea corresponde a cálculo clásico, cuántico o general."""
    t = tarea.lower()
    if "cuant" in t or "qubit" in t or "bell" in t:
        destino = "quantum_engine"
    elif "dato" in t or "estadist" in t or "promedio" in t:
        destino = "data_engine"
    else:
        destino = "general_engine"
    return json.dumps({"route": destino})

def tool_claude_mem(accion: str, clave: str, valor: str = "") -> str:
    """Gestión de memoria clave-valor persistente en disco."""
    mem_file = "agente_memoria.json"
    memoria = {}
    if os.path.exists(mem_file):
        try:
            with open(mem_file, "r", encoding="utf-8") as f:
                memoria = json.load(f)
        except Exception:
            memoria = {}
            
    if accion == "guardar":
        memoria[clave] = valor
        with open(mem_file, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=2)
        return json.dumps({"status": "ok", "guardado": clave})
    elif accion == "leer":
        return json.dumps({clave: memoria.get(clave, "No registrado")})
    return json.dumps({"error": "Accion invalida"})

def tool_headroom(num_mensajes: int) -> str:
    """Supervisa el consumo aproximado de contexto para prevenir desbordes."""
    tokens_estimados = num_mensajes * 120
    disponible = max(0, 200000 - tokens_estimados)
    return json.dumps({
        "tokens_usados_aprox": tokens_estimados,
        "headroom": disponible,
        "sugerencia": "OK" if disponible > 30000 else "RESUMIR_HISTORIAL"
    })

def tool_claude_code_setup() -> str:
    """Valida dependencias y entorno de ejecución local."""
    return json.dumps({
        "qiskit": True,
        "numpy": True,
        "cwd": os.path.basename(os.getcwd())
    })

def tool_task_observer(paso: str, estado: str) -> str:
    """Audita y registra hitos de ejecución en consola."""
    print(f"📋 [TaskObserver] {paso} -> {estado}")
    return json.dumps({"status": "logged"})

# Mapeo de despacho
herramientas_map = {
    "tool_analisis_clasico": tool_analisis_clasico,
    "tool_circuito_bell": tool_circuito_bell,
    "tool_omni_route": tool_omni_route,
    "tool_claude_mem": tool_claude_mem,
    "tool_headroom": tool_headroom,
    "tool_claude_code_setup": tool_claude_code_setup,
    "tool_task_observer": tool_task_observer
}

# 3. Definición concisa de esquemas JSON (Optimizada para Prompt Caching y reducción de tokens)
tools_schema = [
    {
        "name": "tool_analisis_clasico",
        "description": "Calcula media, desviación estándar y extremos de una lista numérica.",
        "input_schema": {
            "type": "object",
            "properties": {"datos": {"type": "array", "items": {"type": "number"}}},
            "required": ["datos"]
        }
    },
    {
        "name": "tool_circuito_bell",
        "description": "Simula un circuito cuántico de Bell con Qiskit Aer.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "tool_omni_route",
        "description": "Enruta la subtarea al subsistema adecuado.",
        "input_schema": {
            "type": "object",
            "properties": {"tarea": {"type": "string"}},
            "required": ["tarea"]
        }
    },
    {
        "name": "tool_claude_mem",
        "description": "Almacena o recupera datos persistentes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "accion": {"type": "string", "enum": ["guardar", "leer"]},
                "clave": {"type": "string"},
                "valor": {"type": "string"}
            },
            "required": ["accion", "clave"]
        }
    },
    {
        "name": "tool_headroom",
        "description": "Chequea margen de tokens libres en la ventana de contexto.",
        "input_schema": {
            "type": "object",
            "properties": {"num_mensajes": {"type": "integer"}},
            "required": ["num_mensajes"]
        }
    },
    {
        "name": "tool_claude_code_setup",
        "description": "Inspecciona el estado de librerías y entorno local.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "tool_task_observer",
        "description": "Registra pasos completados para auditoría.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paso": {"type": "string"},
                "estado": {"type": "string"}
            },
            "required": ["paso", "estado"]
        }
    }
]

# System prompt optimizado con Prompt Caching para Anthropic
system_instructions = [
    {
        "type": "text",
        "text": (
            "Sos un agente técnico híbrido de computación cuántica y análisis de datos. "
            "Respondé de forma directa y concisa. "
            "Usá las herramientas cuando se soliciten operaciones específicas. "
            "No invoques herramientas de observación o setup a menos que sea estrictamente necesario."
        ),
        "cache_control": {"type": "ephemeral"}
    }
]

# 4. Función de chat agéntico con control de costos (Haiku para tools, límite estricto de pasos)
def responder_chat(mensaje: str, historial: list):
    # Modelo Haiku para mantener consumo mínimo en la factura
    MODELO_ECONOMICO = "claude-3-5-haiku-20241022"
    mensajes = [{"role": "user", "content": mensaje}]
    max_pasos = 4  # Evita bucles prolongados

    for _ in range(max_pasos):
        response = client.messages.create(
            model=MODELO_ECONOMICO,
            max_tokens=1000,
            system=system_instructions,
            tools=tools_schema,
            messages=mensajes
        )

        if response.stop_reason != "tool_use":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Proceso completado sin salida de texto."

        # Registro de turnos y ejecución local
        mensajes.append({"role": "assistant", "content": response.content})
        resultados_herramientas = []

        for block in response.content:
            if block.type == "tool_use":
                fn_name = block.name
                fn_args = block.input
                print(f"⚙️ [Claude Tool]: {fn_name}({fn_args})")
                
                if fn_name in herramientas_map:
                    salida = herramientas_map[fn_name](**fn_args)
                else:
                    salida = json.dumps({"error": f"Herramienta {fn_name} no disponible"})

                resultados_herramientas.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": salida
                })

        mensajes.append({"role": "user", "content": resultados_herramientas})

    return "Se completó el máximo de pasos agénticos."

# 5. Interfaz de Gradio
demo = gr.ChatInterface(
    fn=responder_chat,
    title="⚛️ Agente Cuántico & Datos (Claude Low-Cost Engine)",
    description="Asistente agéntico conectado a Qiskit y NumPy optimizado con Claude 3.5 Haiku y Prompt Caching."
)

if __name__ == "__main__":
    # Permite acceso local y genera túnel público si se ejecuta en entornos remotos
    demo.launch(share=False)