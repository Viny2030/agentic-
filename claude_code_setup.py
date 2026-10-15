"""
Claude Code Setup
Herramienta de configuración del entorno: verifica dependencias, rutas
de repositorios, variables de entorno y herramientas de desarrollo.
"""
import os
import sys
import json
import importlib

def tool_claude_code_setup(accion: str = "verificar_todo") -> str:
    """
    Audita librerías instaladas, versiones de runtime y disponibilidad de API keys.
    """
    librerias = ["anthropic", "qiskit", "qiskit_aer", "numpy", "gradio"]
    res_libs = {}
    for lib in librerias:
        try:
            m = importlib.import_module(lib)
            res_libs[lib] = {"instalado": True, "version": getattr(m, "__version__", "ok")}
        except ImportError:
            res_libs[lib] = {"instalado": False, "version": None}

    claves = ["ANTHROPIC_API_KEY", "IONQ_API_KEY", "IBM_QUANTUM_TOKEN"]
    res_claves = {c: ("Configurada" if os.environ.get(c) else "Faltante") for c in claves}

    diagnostico = {
        "python_version": sys.version.split()[0],
        "plataforma": sys.platform,
        "directorio_trabajo": os.getcwd(),
        "paquetes_criticos": res_libs,
        "credenciales_detectadas": res_claves
    }

    if accion == "verificar_librerias":
        return json.dumps(res_libs, indent=2)
    elif accion == "verificar_claves":
        return json.dumps(res_claves, indent=2)

    return json.dumps(diagnostico, indent=2)

schema_claude_code_setup = {
    "name": "tool_claude_code_setup",
    "description": "Verifica paquetes, entorno de desarrollo y variables de entorno del sistema.",
    "input_schema": {
        "type": "object",
        "properties": {
            "accion": {
                "type": "string",
                "enum": ["verificar_todo", "verificar_librerias", "verificar_claves"],
                "default": "verificar_todo"
            }
        }
    }
}
