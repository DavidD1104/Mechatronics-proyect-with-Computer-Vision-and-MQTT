"""
Inferencia en tiempo real usando cámara
Modelo entrenado con YOLOv8
"""

import cv2
from ultralytics import YOLO
import time

# -----------------------------
# Cargar modelo entrenado
# -----------------------------
MODEL_PATH = "runs/detect/train4/weights/best.pt"
model = YOLO(MODEL_PATH)

# -----------------------------
# Inicializar cámara
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise IOError("No se puede abrir la cámara")

# FPS
prev_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Inferencia
    results = model(frame, conf=0.5)

    # Procesar resultados
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            label = f"{model.names[cls_id]} {conf:.2f}"

            # Dibujar bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # -----------------------------
            # MQTT (DESACTIVADO POR AHORA)
            # -----------------------------
            """
            mensaje = {
                "pieza": model.names[cls_id],
                "confianza": round(conf, 2)
            }
            client.publish("vision/pieza", json.dumps(mensaje))
            """

    # FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time else 0
    prev_time = current_time
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        2
    )

    # Mostrar imagen
    cv2.imshow("YOLOv8 - Vision Mecatronica", frame)

    # ESC para salir
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
