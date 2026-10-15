"""
Claude Mem
Sistema de memoria persistente a largo plazo: lee y guarda preferencias,
estado de proyectos y aprendizajes en archivos locales JSON o vectores.
"""
import os
import json
from datetime import datetime

ARCHIVO_MEMORIA = "memoria_agente.json"

def _cargar():
    if os.path.exists(ARCHIVO_MEMORIA):
        try:
            with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _guardar(data):
    with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def tool_claude_mem(accion: str, clave: str, valor: str = "") -> str:
    """
    Gestiona la memoria persistente del agente entre sesiones.
    """
    mem = _cargar()

    if accion == "guardar":
        if not valor:
            return json.dumps({"error": "Debe especificar un valor a persistir."})
        mem[clave] = {
            "valor": valor,
            "timestamp": datetime.now().isoformat()
        }
        _guardar(mem)
        return json.dumps({"status": "guardado_exitoso", "clave": clave})

    elif accion == "leer":
        if clave in mem:
            return json.dumps({"clave": clave, "registro": mem[clave]}, ensure_ascii=False)
        return json.dumps({"status": "no_encontrado", "clave": clave})

    elif accion == "listar":
        return json.dumps({"claves_disponibles": list(mem.keys())})

    elif accion == "borrar":
        if clave in mem:
            del mem[clave]
            _guardar(mem)
            return json.dumps({"status": "borrado", "clave": clave})
        return json.dumps({"status": "no_existe", "clave": clave})

    return json.dumps({"error": f"Acción inválida: {accion}"})

schema_claude_mem = {
    "name": "tool_claude_mem",
    "description": "Memoria persistente a largo plazo: guarda o consulta configuraciones y estado entre ejecuciones.",
    "input_schema": {
        "type": "object",
        "properties": {
            "accion": {"type": "string", "enum": ["guardar", "leer", "listar", "borrar"]},
            "clave": {"type": "string", "description": "Identificador único o tema."},
            "valor": {"type": "string", "description": "Contenido a guardar (obligatorio en 'guardar')."}
        },
        "required": ["accion", "clave"]
    }
}
