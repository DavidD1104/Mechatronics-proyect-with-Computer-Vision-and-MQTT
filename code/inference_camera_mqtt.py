"""
Inferencia en tiempo real usando cámara
YOLOv8 + envío MQTT del tipo de pieza
"""

import cv2
import time
import paho.mqtt.client as mqtt
from ultralytics import YOLO

# -----------------------------
# CONFIGURACIÓN MQTT
# -----------------------------
MQTT_BROKER = "broker.hivemq.com"     # igual que en mqtt.py
MQTT_PORT = 1883                  # igual que en mqtt.py
MQTT_TOPIC = "vision/pieza"
MQTT_CLIENT_ID = "esp32_G7_camara"

# -----------------------------
# MQTT
# -----------------------------
client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()
print("✅ MQTT conectado")

# -----------------------------
# MODELO YOLO
# -----------------------------
MODEL_PATH = "runs/detect/train4/weights/best.pt"
model = YOLO(MODEL_PATH)

# -----------------------------
# CÁMARA
# -----------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("No se puede abrir la cámara")

prev_time = 0
ultima_pieza_enviada = None
TIEMPO_MIN_ENTRE_ENVIO = 2.0  # segundos
ultimo_envio_time = 0


# -----------------------------
# LOOP PRINCIPAL
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.5)
    pieza_detectada = None

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            pieza_detectada = model.names[cls_id]   # ← pieza_cuadrado / triangulo / circulo

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = f"{pieza_detectada} {conf:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            break  # solo una detección

    # -----------------------------
    # MQTT: enviar solo si cambia
    # -----------------------------
    if pieza_detectada and pieza_detectada != ultima_pieza_enviada:
        client.publish(MQTT_TOPIC, pieza_detectada)
        print(f"📤 Enviado MQTT → {pieza_detectada}")
        ultima_pieza_enviada = pieza_detectada

    # -----------------------------
    # FPS
    # -----------------------------
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time else 0
    prev_time = current_time
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("YOLOv8 - Vision Mecatronica", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# -----------------------------
# CIERRE
# -----------------------------
cap.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
print("🔌 MQTT desconectado")
