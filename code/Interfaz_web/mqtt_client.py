# mqtt_client.py
import json
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883

estado_sistema = {
    "estado": "STOP",
    "modo": "MANUAL",
    "piezas": 0,
    "ultima_pieza": None
}

def on_message(client, userdata, msg):
    global estado_sistema

    try:
        payload = msg.payload.decode()

        # -------- ESTADO GENERAL (JSON) --------
        if msg.topic == "sistema/estado":
            data = json.loads(payload)
            estado_sistema["estado"] = data.get("estado")
            estado_sistema["modo"] = data.get("modo")
            estado_sistema["piezas"] = data.get("piezas")

        # -------- VISIÓN (TEXTO PLANO) --------
        elif msg.topic == "vision/pieza":
            estado_sistema["ultima_pieza"] = payload

    except Exception as e:
        print("❌ Error MQTT:", e, " | payload:", payload)


def iniciar_mqtt():
    client = mqtt.Client(
        client_id="backend_python",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION1
    )

    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe("sistema/#")
    client.loop_start()

    print("✅ MQTT backend conectado")

    return client

