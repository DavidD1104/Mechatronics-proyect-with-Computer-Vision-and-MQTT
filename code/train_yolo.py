"""
Entrenamiento de modelo YOLOv8 para clasificación y detección de piezas
Dataset generado con Roboflow
"""

from ultralytics import YOLO
import torch

def main():

    # Comprobación de GPU
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"Usando dispositivo: {device}")

    # Cargar modelo base (ligero y rápido)
    model = YOLO("yolov8n.pt")

    # Entrenamiento
    model.train(
        data="C:/Users/david/Desktop/uni/Cuarto_Primer_cuatri/Mecatrónica/Vision Proyecto Mecatronica/Proyecto Mecatronica.v2-primer-intento.yolov8/data.yaml",
        epochs=60,
        imgsz=640,
        batch=16,
        patience=15,     # early stopping
        optimizer="Adam",
        lr0=0.001,
        device=device,
        workers=4,
        verbose=True
    )

    # Evaluación final sobre test
    model.val(split="test")

if __name__ == "__main__":
    main()
