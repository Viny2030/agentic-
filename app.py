import os
import json
import anthropic
import gradio as gr
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# 1. Cliente Anthropic optimizado (Claude 3.5 Haiku para minimizar costos)
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=API_KEY) if API_KEY else None

MODELO_ECONOMICO = "claude-3-5-haiku-20241022"

# 2. Herramientas Locales (Clásica y Cuántica)
def tool_analisis_clasico(datos: list[float]) -> str:
    arr = np.array(datos)
    return json.dumps({
        "media": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr))
    })

def tool_circuito_bell() -> str:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    sim = AerSimulator()
    job = sim.run(qc, shots=1000)
    return json.dumps({"shots": 1000, "conteo": job.result().get_counts()})

# 3. Herramientas de Control y Memoria
def tool_omni_route(tarea: str) -> str:
    destino = "cuantico" if "cuant" in tarea.lower() or "qubit" in tarea.lower() else "clasico"
    return json.dumps({"ruta": destino})

def tool_claude_mem(accion: str, clave: str, valor: str = "") -> str:
    archivo = "memoria_agente.json"
    mem = {}
    if os.path.exists(archivo):
        try:
            with open(archivo, "r") as f:
                mem = json.load(f)
        except Exception:
            mem = {}
    if accion == "guardar":
        mem[clave] = valor
        with open(archivo, "w") as f:
            json.dump(mem, f, indent=2)
        return json.dumps({"status": "guardado", "clave": clave})
    return json.dumps({"clave": clave, "valor": mem.get(clave, "vacio")})

def tool_headroom(turnos: int) -> str:
    disponible = max(0, 200000 - (turnos * 150))
    return json.dumps({"headroom": disponible, "estado": "OK" if disponible > 30000 else "ALERT"})

def tool_task_observer(paso: str, detalle: str) -> str:
    print(f"[OBSERVER] {paso}: {detalle}")
    return json.dumps({"log": f"{paso}: {detalle}"})

herramientas_map = {
    "tool_analisis_clasico": tool_analisis_clasico,
    "tool_circuito_bell": tool_circuito_bell,
    "tool_omni_route": tool_omni_route,
    "tool_claude_mem": tool_claude_mem,
    "tool_headroom": tool_headroom,
    "tool_task_observer": tool_task_observer
}

# 4. Esquema conciso de herramientas (Token-efficient)
tools_schema = [
    {
        "name": "tool_analisis_clasico",
        "description": "Calcula media, std, min y max de numeros.",
        "input_schema": {
            "type": "object",
            "properties": {"datos": {"type": "array", "items": {"type": "number"}}},
            "required": ["datos"]
        }
    },
    {
        "name": "tool_circuito_bell",
        "description": "Simula entrelazamiento de Bell con Qiskit.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "tool_omni_route",
        "description": "Enruta subtareas entre clasico y cuantico.",
        "input_schema": {
            "type": "object",
            "properties": {"tarea": {"type": "string"}},
            "required": ["tarea"]
        }
    },
    {
        "name": "tool_claude_mem",
        "description": "Lee o guarda memoria persistente.",
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
        "description": "Verifica tokens libres en contexto.",
        "input_schema": {
            "type": "object",
            "properties": {"turnos": {"type": "integer"}},
            "required": ["turnos"]
        }
    },
    {
        "name": "tool_task_observer",
        "description": "Registra el paso ejecutado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paso": {"type": "string"},
                "detalle": {"type": "string"}
            },
            "required": ["paso", "detalle"]
        }
    }
]

# 5. Bucle Agentic con Prompt Caching
def responder_chat(mensaje, historial):
    if not client:
        return "Configura la variable ANTHROPIC_API_KEY para comenzar."

    mensajes = [{"role": "user", "content": mensaje}]

    # Prompt con cache_control para ahorrar hasta 90% en llamadas subsecuentes
    sistema = [
        {
            "type": "text",
            "text": "Sos un asistente cientifico conciso de datos y computacion cuantica. Usa herramientas cuando sea necesario.",
            "cache_control": {"type": "ephemeral"}
        }
    ]

    for _ in range(5):
        res = client.messages.create(
            model=MODELO_ECONOMICO,
            max_tokens=1024,
            system=sistema,
            tools=tools_schema,
            messages=mensajes
        )

        if res.stop_reason != "tool_use":
            for b in res.content:
                if hasattr(b, "text"):
                    return b.text
            return "Listo."

        mensajes.append({"role": "assistant", "content": res.content})
        resultados = []

        for b in res.content:
            if b.type == "tool_use":
                salida = herramientas_map[b.name](**b.input)
                resultados.append({
                    "type": "tool_result",
                    "tool_use_id": b.id,
                    "content": salida
                })

        mensajes.append({"role": "user", "content": resultados})

    return "Tarea finalizada."

demo = gr.ChatInterface(
    fn=responder_chat,
    title="Asistente Cuantico & Datos (Claude Low-Cost)",
    description="Agente con herramientas clasicas, Qiskit y memoria persistente."
)

if __name__ == "__main__":
    demo.launch()
