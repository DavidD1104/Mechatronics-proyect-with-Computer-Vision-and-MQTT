from fastapi import FastAPI
import paho.mqtt.client as mqtt
import json
from fastapi.staticfiles import StaticFiles

app = FastAPI()


# ---------------- ESTADO GLOBAL ----------------
estado_sistema = {
    "estado": "STOP",
    "modo": "MANUAL",
    "piezas": 0,
    "ultima_pieza": "-"
}

# ---------------- MQTT ----------------
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("✅ MQTT backend conectado")
    client.subscribe("sistema/estado")
    client.subscribe("vision/pieza")

def on_message(client, userdata, msg):
    global estado_sistema
    payload = msg.payload.decode()

    try:
        if msg.topic == "sistema/estado":
            data = json.loads(payload)
            estado_sistema["estado"] = data.get("estado")
            estado_sistema["modo"] = data.get("modo")
            estado_sistema["piezas"] = data.get("piezas")

        elif msg.topic == "vision/pieza":
            estado_sistema["ultima_pieza"] = payload

    except Exception as e:
        print("❌ Error MQTT:", e)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# ---------------- API ----------------

@app.get("/api/estado")
def get_estado():
    return estado_sistema

@app.post("/api/start")
def start():
    mqtt_client.publish("cmd/start", "RUN")
    return {"ok": True}

@app.post("/api/stop")
def stop():
    mqtt_client.publish("cmd/stop", "STOP")
    return {"ok": True}

@app.post("/api/modo/{modo}")
def cambiar_modo(modo: str):
    modo = modo.upper()
    if modo not in ["AUTO", "MANUAL"]:
        return {"error": "Modo no válido"}
    mqtt_client.publish("cmd/modo", modo)
    return {"modo": modo}

app.mount("/", StaticFiles(directory="static", html=True), name="static")