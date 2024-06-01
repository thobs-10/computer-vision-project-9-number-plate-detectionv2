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
    
@app.route('/')
async def root():
    return os.system('python run streamlit.py')

@app.route('/api/v1/predict', methods=['GET','POST'])
async def predict():
    try:
        if requests.request() == 'POST':
            data = await request.json()
            image = data['image']
            image = decode_image(image)
            # we gonna use model from roboflow to detect number plates
            # os.system("cd yolov8/ && python detect.py --weights my_model.pt --img 416 --conf 0.5 --source ../data/inputImage.jpg")
            image = encode_into_base64(image)
            os.system("rm -rf yolov8/runs")
            return {"message": image}
    except ValueError as val:
        print(val)
        return Response("Value not found inside  json data")
    except KeyError:
        return Response("Key value error incorrect key passed")
    except Exception as e:
        print(e)
        result = "Invalid input"
        return jsonify(result)

@app.route('/api/v1/live', methods=['GET'])
async def live():
    # to do live camera detections
    # added nothing
    ##
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


