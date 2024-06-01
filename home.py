import streamlit as st
import requests
from PIL import Image
import io

st.title('Welcome to the Detection App')

option = st.sidebar.selectbox(
    'Choose an option',
    ('Home', 'Live Detection', 'Upload Image for Detection', 'Train Model')
)

if option == 'Home':
    st.write('Welcome to the Detection App. Please choose an option from the sidebar.')


elif option == 'Live Detection':
    st.write('Live Detection')
    if st.button('Start Live Detection'):
        st.video("http://localhost:8000/api/v1/live", format="video/mp4")

elif option == 'Upload Image for Detection':
    st.write('Upload Image for Detection')
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        st.write("")
        st.write("Classifying...")
        
        # Convert the image to bytes
        buf = io.BytesIO()
        image.save(buf, format='JPEG')
        byte_im = buf.getvalue()

        response = requests.post(
            "http://localhost:8000/api/v1/predict",
            files={"file": ("image.jpg", byte_im, "image/jpeg")},
            data={"name": "example", "uuid": "123e4567-e89b-12d3-a456-426614174000"}
        )

        if response.status_code == 200:
            result = response.json()
            st.write(f"Predicted Class: {result['predicted_class']}")
            st.write(f"Prediction Confidence: {result['prediction_confidence']}")
        else:
            st.write("Failed to classify image.")
elif option == 'Train Model':
    st.write('Train Model')
    if st.button('Start Training'):
        response = requests.get("http://localhost:8000/api/v1/train")
        if response.status_code == 200:
            st.write(response.json())
        else:
            st.write("Failed to start training.")