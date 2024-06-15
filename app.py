import sys
import os
from src.pipeline.training_pipeline import TrainingPipeline
from src.exception import AppException
from src.utils.main_utils import decode_image, encode_into_base64
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import List
from uuid import UUID, uuid4, Annotated
import requests
# from flask import Flask, request
from pydantic import BaseModel
from tkinter import Image
from PIL import Image
import numpy as np
import io
import tensorflow as tf
import ultralytics
import cv2

class DataRequest(BaseModel):
    name: str
    uuid: uuid4

async def parse_form_data(
    name: Annotated[str, Form(...)],
    uuid: Annotated[uuid4, Form(...)]
) -> DataRequest:
    return DataRequest(name=name, uuid=uuid)

def preprocess_image(image: Image.Image) -> np.array:
    # preprocess the image to the format expected by the model
    image = image.resize((224, 224))  # Example: resize to 224x224
    image_array = np.array(image)
    image_array = image_array / 255.0  # Example: normalize the image
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
    return image_array

def detect_number_plate_frame(frame):
    results = model(frame)
    detections = results.xyxy[0]  # Get xyxy format bounding boxes

    for detection in detections:
        x1, y1, x2, y2, conf, cls = detection
        if conf > 0.5:  # Confidence threshold
            label = model.names[int(cls)]
            if label == "license plate":
                color = (0, 255, 0)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
    return frame

def generate_frames():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Could not start camera.")
    
    while True:
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError("Could not read frame from camera.")
        
        frame = detect_number_plate_frame(frame)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
    cap.release()



# Load your pre-trained model
model = tf.keras.models.load_model("path_to_your_model.h5")

app = FastAPI()

@app.route("/api/v1/train")
async def train():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return {"message": "Training pipeline completed successfully"}
    except Exception as e:
        raise AppException(e, sys)
    

@app.post("/upload/")
async def upload_file(
    form_data: Annotated[DataRequest, Depends(parse_form_data)],
    file: UploadFile = File(...)
):
    return {
        "name": form_data.name,
        "uuid": str(form_data.uuid),
        "filename": file.filename,
        "content_type": file.content_type
    }

@app.post("/api/v1/predict")
async def predict(
    form_data: Annotated[DataRequest, Depends(parse_form_data)],
    file: UploadFile = File(...)
):
    # Ensure the uploaded file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")
    
    # Read the image file
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    image.save("data/inputImage.jpg")

    # preprocess the image
    preprocessed_image = preprocessed_image(image)
    
    # Make a prediction using the trained model
    prediction = model.predict(preprocessed_image)
    predicted_class = np.argmax(prediction, axis=1)[0]
    
    # Return the prediction as a JSON response
    return {
        "name": form_data.name,
        "uuid": str(form_data.uuid),
        "predicted_class": int(predicted_class),
        "prediction_confidence": float(np.max(prediction))
    }


@app.get('/api/v1/live')
async def live():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)


