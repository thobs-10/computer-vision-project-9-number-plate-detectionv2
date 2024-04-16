# import a utility function for loading Roboflow models
from inference import get_model
# import supervision to visualize our results
import supervision as sv
# import cv2 to helo load our image
import cv2
import streamlit as st
import tempfile

tracker = sv.ByteTrack()
trace_annotator = sv.TraceAnnotator()
box_annotator = sv.BoundingBoxAnnotator()
names = ['number-plate']

class Tracking:
    def __init__(self):
        self.model = None
        self.confidence = 0.5
        self.save_video = False
        self.enable_gpu = False
        self.custom_classes = False
    
    def load_model(self):
        # load a pre-trained yolov8n model
        self.model = get_model(model_id="np_detection-xgvjf/2")
        # return self.model
    
    def model_predictions(self, image):
        # run inference on our chosen image, image can be a url, a numpy array, a PIL image, etc.
        results = self.model.infer(image)
        # load the results into the supervision Detections api
        detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))

        # create supervision annotators
        bounding_box_annotator = sv.BoundingBoxAnnotator()
        label_annotator = sv.LabelAnnotator()

        # annotate the image with our inference results
        annotated_image = bounding_box_annotator.annotate(
            scene=image, detections=detections)
        annotated_image = label_annotator.annotate(
            scene=annotated_image, detections=detections)

        # display the image
        # sv.plot_image(annotated_image)
        return annotated_image
    
    def load_and_process_frames(self, video_file):
        # read the video file
        cap = cv2.VideoCapture(video_file)
        while cap.isOpened():
            # read the frame
            ok, frame = cap.read()
            self.load_model()
            if ok:
                # process the frame
                annotated_img = self.model_predictions(frame)
                # display the frame
                # sv.plot_image(annotated_img)
                # yield annotated_img
                detections = sv.Detections.from_ultralytics(annotated_img[0])
                detections = tracker.update_with_detections(detections)


def main():
    st.title('Number-plate Tracking')

    detection_file = 'data\\test_video_3.mp4'
    tfflie = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    vid = cv2.VideoCapture(detection_file)
    tfflie.name = detection_file
    demo_vid = open(tfflie.name, 'rb')
    
    st.sidebar.title('Settings')
    
    st.markdown(
        """
        <style>
        [data-testid = "stSidebar"][aria-expanded="true"] > div:first-child{width: 340px;}
        [data-testid = "stSidebar"][aria-expanded="false"] > div:first-child{width: 340px; margin-left: -340px}
        </style>
        """,
        unsafe_allow_html=True,
    )
    # st.sidebar.markdown('---')
    confidence = st.sidebar.slider('confidence level',min_value=0,max_value=100, value= 50)
    st.sidebar.markdown('---')
    save_video = st.sidebar.checkbox('Save Video')
    enable_gpu = st.sidebar.checkbox('Enable GPU')
    custom_classes = st.sidebar.checkbox('Use Custom Classes')

    assigned_class_ids = []

    if custom_classes:
        assiigned_classes = st.sidebar.multiselect('Select Custom Class', list(names), default='number-plate')
        for each_class in assiigned_classes:
            assigned_class_ids.append(names.index(each_class))

    # angles of interest
#     angle = st.sidebar.radio(
#     "Angle of interest?",
#     ["Spine", "Arms", "leg stand"],
#     index=None,
# )
    # uploading video files
    video_file_buffer = st.sidebar.file_uploader('upload video', type=['mp4','mov','avi','m4v','asf'])
    demo_file = 'data\\test_video_3.mp4'
    tfflie = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)

    # get input video
    if not video_file_buffer:
        vid = cv2.VideoCapture(demo_file)
        tfflie.name = demo_file
        demo_vid = open(tfflie.name, 'rb')
        demo_bytes = demo_vid.read()

        st.sidebar.text('Input Video')
        st.sidebar.video(demo_bytes)
    
    else:
        tfflie.write(video_file_buffer.read())
        demo_vid = open(tfflie.name, 'rb')
        demo_bytes = demo_vid.read()

        st.sidebar.text('Input Video')
        st.sidebar.video(demo_bytes)

    print(tfflie.name)
    stFrame = st.empty()
    st.sidebar.markdown('---')

    angle1, angle2, angle3 = st.columns(3)

    with angle1:
        st.markdown('**Incoming**')
        angle_val = st.markdown('0')
    with angle2:
        st.markdown('**Outgoing**')
        angle_val = st.markdown('0')
    # with angle3:
    #     st.markdown('**ball Estimated landing time**')
    #     angle_val = st.markdown('0 ms')

    frame_placeholder = st.empty()
    # display the tracked video during inference
    # canvas, gray_init_frame = club_tracking.create_canvas(vid)
    # result_frame = club_tracking.load_and_process_video(vid, canvas, gray_init_frame)
    # frame_placeholder.image(result_frame, width=700 ,channels="BGR")
    # vid.release()
    # cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass