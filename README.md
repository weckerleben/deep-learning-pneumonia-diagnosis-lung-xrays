# NeumoScan — Deep Learning Pneumonia Diagnosis from Lung X-rays

Sistema end-to-end de diagnóstico de neumonía en radiografías de tórax mediante deep learning. Clasifica imágenes en **tres categorías**: Normal, Neumonía Bacteriana y Neumonía Viral.

**Stack:** FastAI · PyTorch · ResNet50 · Flask · Android (Kotlin + Jetpack Compose) · Docker

---

## Arquitectura

```
chest_xray/
  train/ → model.py (ResNet50 fine-tuning) → model.pkl
                                                  ↓
                                           api/app.py (Flask REST)
                                                  ↓
                                     NeumoScan (Android app)
```

---

## Dataset

[Chest X-Ray Images (Pneumonia)](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) — Kaggle

| Split | NORMAL | BACTERIAL | VIRAL | Total |
|-------|--------|-----------|-------|-------|
| Train | ~1,341 | ~2,530 | ~1,345 | ~5,216 |
| Val | 8 | 8 | 8 | 24 |
| Test | 234 | 242 | 148 | 624 |

---

## Instalación

```bash
git clone <repo>
cd deep-learning-pneumonia-diagnosis-lung-xrays

pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

---

## Entrenamiento

```bash
cd model
python src/main.py
```

El script ejecuta:
1. Carga de datos con augmentación (`aug_transforms`)
2. Cálculo de class weights para manejar el desbalance
3. Fase 1: 3 épocas con backbone congelado (solo el head)
4. Fase 2: 7 épocas con fine-tuning completo y LR diferenciado
5. Exporta `trained_model/model.pkl`

**Learning Rate Finder** (opcional, descomentar en `model.py`):
```python
learn.lr_find()  # Genera gráfica — buscar el punto de mayor pendiente negativa
```

---

## Evaluación

```bash
cd model
python test.py --model trained_model/model.pkl --test-path chest_xray/test
```

Genera:
- `confusion_matrix.png` — matriz de confusión por clase
- `top_losses.png` — las 9 peores predicciones
- `test_results.txt` — classification report completo (precision/recall/F1 por clase)

**Resultados reportados:** 95% de accuracy en test set.

---

## Explicabilidad — Grad-CAM

Visualiza qué regiones de la radiografía activaron la predicción:

```bash
cd model

# Una imagen
python gradcam.py --model trained_model/model.pkl --image chest_xray/test/PNEUMONIA/rx.jpg

# Una carpeta completa
python gradcam.py --model trained_model/model.pkl --folder chest_xray/test/NORMAL --n 10
```

Genera imágenes en `gradcam_output/` con el heatmap superpuesto a la RX.

---

## Preprocessing opcional — CLAHE

Mejora el contraste de radiografías antes del entrenamiento:

```bash
cd model
python src/utils/clahe_preprocess.py --input chest_xray/train --output chest_xray_clahe/train
```

---

## Export multi-formato

```bash
cd model
python -m src.model.model_converter
```

Genera:
- `trained_model/model.pt` — PyTorch state dict
- `trained_model/model.onnx` — ONNX para inferencia cross-platform

---

## API REST

### Con Docker (recomendado)

```bash
cp .env.example .env   # Configurar variables
docker-compose up --build
```

### Manual

```bash
cd api
API_HOST=0.0.0.0 API_PORT=1796 python app.py
```

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health-check` | Estado del servidor |
| `POST` | `/neumoscan` | Analizar radiografía |

**POST /neumoscan** — `multipart/form-data`
```
imagen: <archivo de imagen>  (.jpg, .jpeg, .png, .bmp, .tiff, max 15MB)
```

**Respuesta:**
```json
{
  "file": "rx.jpg",
  "prediction": "BACTERIAL_PNEUMONIA",
  "probability": 0.9734
}
```

Si la confianza es menor al 70% (configurable con `CONFIDENCE_THRESHOLD`):
```json
{
  "prediction": "INCONCLUSIVE",
  "probability": 0.5100,
  "message": "Confianza insuficiente. Se requiere radiografía de mayor calidad."
}
```

Documentación Swagger: `http://localhost:1796/apidocs`

---

## App Android

La app **NeumoScan** permite capturar o seleccionar una radiografía y enviarla a la API.

**Configurar la URL del servidor** en `NeumoScan/app/src/main/res/values/strings.xml`:
```xml
<string name="api_base_url">http://TU_IP:1796</string>
```

**Colores de resultado:**
- Verde → NORMAL
- Rojo → BACTERIAL PNEUMONIA
- Naranja → VIRAL PNEUMONIA
- Gris → INCONCLUSIVE

---

## Variables de entorno

Copiar `.env.example` a `.env` y configurar:

| Variable | Descripción | Default |
|----------|-------------|---------|
| `API_HOST` | IP del servidor | `0.0.0.0` |
| `API_PORT` | Puerto de la API | `1796` |
| `CONFIDENCE_THRESHOLD` | Mínimo de confianza para dar diagnóstico | `0.70` |
| `TWILIO_SID` | Twilio Account SID | — |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | — |
| `TWILIO_NUMBER` | Número Twilio origen | — |
| `TWILIO_RECIPIENT` | Número destino SMS | — |
| `GMAIL_USER` | Correo Gmail | — |
| `GMAIL_APP_PASSWORD` | App Password de Gmail | — |
| `EMAIL_RECIPIENT` | Correo destino notificaciones | — |

---

## Referencias

- [FastAI](https://www.fast.ai/)
- [ResNet50 — Deep Residual Learning](https://arxiv.org/abs/1512.03385)
- [Grad-CAM — Visual Explanations](https://arxiv.org/abs/1610.02391)
- [Dataset — Kaggle Chest X-Ray](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia)
