"""
Headroom
Monitor y gestor de la ventana de contexto: calcula cuántos tokens quedan
disponibles para resumir o podar el historial antes de desbordar el contexto.
"""
import json

def tool_headroom(turnos_historial: int, tokens_estimados: int = 0) -> str:
    """
    Monitorea el consumo de la ventana de contexto para evitar desbordes y regular costos.
    """
    LIMITE_MAXIMO = 200000  # Ventana típica de Claude 3.5 / 3.7
    
    consumo = tokens_estimados if tokens_estimados > 0 else (turnos_historial * 220)
    tokens_restantes = max(0, LIMITE_MAXIMO - consumo)
    porcentaje = (consumo / LIMITE_MAXIMO) * 100

    if tokens_restantes > 100000:
        alerta = "VERDE_OPTIMO"
        accion = "Margen de contexto amplio. No requiere poda."
    elif tokens_restantes > 40000:
        alerta = "AMARILLO_MODERADO"
        accion = "Monitorear tamaño de respuestas y evitar outputs masivos."
    else:
        alerta = "ROJO_CRITICO"
        accion = "Peligro de desbordamiento. Ejecutar poda o resumen de mensajes anteriores."

    return json.dumps({
        "tokens_usados_aprox": consumo,
        "headroom_disponible": tokens_restantes,
        "uso_porcentual": f"{porcentaje:.2f}%",
        "alerta": alerta,
        "recomendacion": accion
    }, ensure_ascii=False)

schema_headroom = {
    "name": "tool_headroom",
    "description": "Calcula tokens disponibles y alerta si se debe podar el historial para evitar desbordes.",
    "input_schema": {
        "type": "object",
        "properties": {
            "turnos_historial": {"type": "integer", "description": "Cantidad de turnos acumulados en la conversación."},
            "tokens_estimados": {"type": "integer", "description": "Tokens consumidos exactos o calculados."}
        },
        "required": ["turnos_historial"]
    }
}
