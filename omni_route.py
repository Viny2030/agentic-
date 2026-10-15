"""
Omni Route
Enrutador de intenciones o modelos: decide si una subtarea va a un modelo rápido (Haiku),
a un subagente especializado (clásico/cuántico) o a un script específico.
"""
import json

def tool_omni_route(tarea: str, complejidad: str = "auto") -> str:
    """
    Enruta la tarea al modelo o subagente óptimo para minimizar costo y latencia.
    """
    t = tarea.lower()
    
    # Detección cuántica
    if any(k in t for k in ["cuant", "qubit", "bell", "qiskit", "ionq", "entrelazamiento"]):
        subagente = "subagente_cuantico"
        modelo = "claude-3-5-haiku-20241022"
        tipo = "simulador_o_qpu"
    # Detección estadística / análisis clásico
    elif any(k in t for k in ["estadíst", "media", "std", "datos", "numpy", "pandas", "varianza"]):
        subagente = "subagente_clasico"
        modelo = "claude-3-5-haiku-20241022"
        tipo = "script_numpy"
    # Tarea reflexiva / razonamiento profundo
    elif any(k in t for k in ["teoria", "explica detalladamente", "arquitectura", "diseña"]):
        subagente = "analizador_profundo"
        modelo = "claude-3-7-sonnet-20250219" if complejidad in ["alta", "auto"] else "claude-3-5-haiku-20241022"
        tipo = "sintesis_cognitiva"
    else:
        subagente = "ejecutor_general"
        modelo = "claude-3-5-haiku-20241022"
        tipo = "pipeline_estandar"

    return json.dumps({
        "status": "enrutado",
        "tarea": tarea,
        "subagente_asignado": subagente,
        "modelo_asignado": modelo,
        "tipo_ejecucion": tipo
    }, ensure_ascii=False)

schema_omni_route = {
    "name": "tool_omni_route",
    "description": "Enruta la subtarea al modelo o ejecutor óptimo (Haiku vs Sonnet, clásico vs cuántico).",
    "input_schema": {
        "type": "object",
        "properties": {
            "tarea": {"type": "string", "description": "Descripción o intención de la subtarea."},
            "complejidad": {"type": "string", "enum": ["baja", "media", "alta", "auto"], "default": "auto"}
        },
        "required": ["tarea"]
    }
}
