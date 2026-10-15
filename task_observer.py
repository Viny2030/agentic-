"""
Task Observer
Observador y logger de ejecución: registra pasos, valida si los objetivos
se cumplieron y detecta bucles infinitos o fallos repetitivos.
"""
import json
import time

_HISTORIAL_LOGS = []

def tool_task_observer(id_tarea: str, estado: str, detalle: str) -> str:
    """
    Registra y audita el progreso de cada subtarea para garantizar control y prevenir bucles.
    """
    global _HISTORIAL_LOGS

    registro = {
        "tiempo": time.time(),
        "tarea_id": id_tarea,
        "estado": estado,
        "detalle": detalle
    }
    _HISTORIAL_LOGS.append(registro)

    print(f"[TASK OBSERVER] [{estado.upper()}] ({id_tarea}): {detalle}")

    # Análisis de bucles: si los últimos 3 detalles son idénticos
    ultimos = [r["detalle"] for r in _HISTORIAL_LOGS[-3:]]
    es_bucle = len(ultimos) == 3 and len(set(ultimos)) == 1

    return json.dumps({
        "status": "registrado",
        "tarea_id": id_tarea,
        "estado": estado,
        "bucle_detectado": es_bucle,
        "total_eventos": len(_HISTORIAL_LOGS)
    }, ensure_ascii=False)

schema_task_observer = {
    "name": "tool_task_observer",
    "description": "Observador que registra el avance de cada tarea y detecta posibles bucles o fallos.",
    "input_schema": {
        "type": "object",
        "properties": {
            "id_tarea": {"type": "string", "description": "Identificador o nombre de la subtarea."},
            "estado": {"type": "string", "enum": ["iniciado", "en_progreso", "completado", "fallido"]},
            "detalle": {"type": "string", "description": "Descripción concisa de la acción ejecutada."}
        },
        "required": ["id_tarea", "estado", "detalle"]
    }
}
