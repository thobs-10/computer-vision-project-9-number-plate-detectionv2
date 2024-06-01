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


