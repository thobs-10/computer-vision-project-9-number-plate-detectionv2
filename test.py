# import a utility function for loading Roboflow models
from inference import get_model
from inference.models.utils import get_model
# import supervision to visualize our results
import supervision as sv
# import cv2 to helo load our image
import cv2
import streamlit as st
import tempfile
import numpy as np
from collections import defaultdict
import sys

tracker = sv.ByteTrack()
trace_annotator = sv.TraceAnnotator()
box_annotator = sv.BoundingBoxAnnotator()
names = ['number-plate']
frame_placeholder = st.empty()

class Tracking:
    def __init__(self):
        self.model = None
        self.confidence = 0.5
        self.save_video = False
        self.enable_gpu = False
        self.custom_classes = False
        # Store the track history
        self.track_history = defaultdict(lambda: [])
        self.detection_id = -1
        self.counter = 0
        self.timestamp = 0
        self.old_center_x = 0
        self.old_center_y = 0
        self.old_x = 0
        self.old_y = 0

        # initialize variables updated by function
        self.selected_point = False
        self.point = ()
        self.old_points = ([[]])

        # set min size of tracked object, e.g. 15x15px
        self.parameter_lucas_kanade = dict(winSize=(15, 15), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS |
                                                                    cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    def select_point(self, event, x, y, flags, params):
        global point, selected_point, old_points
        # record coordinates of mouse click
        if event == cv2.EVENT_LBUTTONDOWN:
            point = (x, y)
            selected_point = True
            old_points = np.array([[x, y]], dtype=np.float32)

    def create_canvas(self, cap):
        # associate select function with window Selector
        cv2.namedWindow('Optical Flow')
        # first frame from stream
        ok, frame = cap.read()
        if not ok:
            print("[ERROR] cannot get frame from video")
            sys.exit()
        # resize the frame 
        frame = cv2.resize(frame, (600, 600))
        # convert to grayscale
        frame_gray_init = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        print(type(frame_gray_init))
        # create a black canvas the size of the initial frame
        canvas = np.zeros_like(frame)
        return canvas, frame_gray_init
    
    def load_model(self):
        # load a pre-trained yolov8n model
        self.model = get_model(model_id="np_detection-xgvjf/2", api_key="JNpKfUfRAHAT2TTAYjnW")
        # return self.model
    
    def model_predictions(self, image):
        # run inference on our chosen image, image can be a url, a numpy array, a PIL image, etc.
        results = self.model.infer(image)[0]
        # load the results into the supervision Detections api
        detections = sv.Detections.from_roboflow(results)

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
        return annotated_image, results, detections
    
    def load_and_process_frames(self, video_file,canvas, gray_init_frame):
        # read the video file
        cap = cv2.VideoCapture(video_file)
        while cap.isOpened():
            self.load_model()
            # read the frame
            ok, frame = cap.read()
            if ok:
                # process the frame
                annotated_img, results, detections = self.model_predictions(frame)
                # display the frame
                # sv.plot_image(annotated_img)
                # yield annotated_img
                # detections = sv.Detections.from_roboflow(results)
                detections = tracker.update_with_detections(detections)
                # work with the frame if error is detected
                i = 0
                bouding_box_conf = results[0].boxes.conf.tolist()
                print(bouding_box_conf)
                if len(bouding_box_conf) > 0:
                    for i in range(len(bouding_box_conf)):
                        if  bouding_box_conf[i]*100 > 20.0:
                            boxes = results[0].boxes.xyxy
                            print(results[0].boxes)
                            numpy_boxes = np.array(results[0].boxes.xyxy)
                            num_of_axis = np.size(numpy_boxes,0)
                            if num_of_axis > 1:
                                pass
                            else:
                                boxes_list = numpy_boxes.tolist()
                                print(boxes_list)
                                self.counter += num_of_axis
                                track_ids = [detection_id + self.counter + 1 for detection_id in range(num_of_axis)]
                                # track_ids = results[0].boxes.id.tolist()
                                print(track_ids)
                                
                                # Visualize the results on the frame
                                annotated_frame = results[0].plot()
                                # covert to grayscale
                                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                # Plot the tracks
                                if self.timestamp == 0:

                                    point = self.old_x, self.old_y
                                    for box, track_id in zip(boxes_list, track_ids):
                                        x1, y1, x2, y2 = box
                                        # calculate the centroid of the bounding box
                                        center_x = int((x1+x2)/2)
                                        center_y = int((y1+y2)/2)
                                        # draw the point in the center of the bounding box
                                        cv2.circle(frame, (int(center_x), int(center_y)), 5, (0, 255, 0), -1)
                                        # update object corners by comparing with found edges in initial frame
                                        old_points = np.array([[center_x, center_y]], dtype=np.float32)
                                        new_points, status, errors = cv2.calcOpticalFlowPyrLK(frame_gray_init, frame_gray, old_points, None,
                                                                                    **self.parameter_lucas_kanade)
                                        print(f"new point: {new_points}")
                                        # overwrite initial frame with current before restarting the loop
                                        frame_gray_init = frame_gray.copy()

                                        print('box: {0}, id: {1}'.format(box, track_id))
                                        track = self.track_history[track_id]
                                        track.append((float(x1), float(y1)))  # x, y center point
                                        if len(track) > 90:  # retain 90 tracks for 90 frames
                                            track.pop(0)
                                        
                                        # Draw the tracking lines
                                        points = np.hstack(numpy_boxes).astype(np.int32).reshape((-1, 1, 2))
                                        print(points)
                                        old_points = new_points
                                        new_x, new_y = new_points.ravel()
                                        j, k = old_points.ravel()

                                    # update time stamp
                                    self.timestamp +=1
                                    old_center_x = center_x
                                    old_center_y = center_y

                                    canvas = cv2.line(canvas,(int(old_center_x), int(old_center_y)), (int(new_x), int(new_y)), (0, 0, 255), 8)
                                    annotated_frame = cv2.circle(annotated_frame, (int(self.old_x), int(self.old_y)), 5, (0, 255, 0), -1)
                                else:
                                    point = self.old_x, self.old_y
                                    for box, track_id in zip(boxes_list, track_ids):
                                        x1, y1, x2, y2 = box
                                        # calculate the centroid of the bounding box
                                        center_x = int((x1+x2)/2)
                                        center_y = int((y1+y2)/2)
                                        # draw the point in the center of the bounding box
                                        cv2.circle(frame, (int(center_x), int(center_y)), 5, (0, 255, 0), -1)
                                        # update object corners by comparing with found edges in initial frame
                                        old_points = np.array([[center_x, center_y]], dtype=np.float32)
                                        new_points, status, errors = cv2.calcOpticalFlowPyrLK(frame_gray_init, frame_gray, old_points, None,
                                                                                    **self.parameter_lucas_kanade)
                                        print(f"new point: {new_points}")
                                        # overwrite initial frame with current before restarting the loop
                                        frame_gray_init = frame_gray.copy()

                                        print('box: {0}, id: {1}'.format(box, track_id))
                                        track = self.track_history[track_id]
                                        track.append((float(x1), float(y1)))  # x, y center point
                                        if len(track) > 90:  # retain 90 tracks for 90 frames
                                            track.pop(0)
                                        
                                        # Draw the tracking lines
                                        points = np.hstack(numpy_boxes).astype(np.int32).reshape((-1, 1, 2))
                                        print(points)
                                        old_points = new_points
                                        new_center_x, new_center_y = new_points.ravel()
                                        j, k = old_points.ravel()
                                        
                                        

                                    canvas = cv2.line(canvas,(int(old_center_x), int(old_center_y)), (int(new_center_x), int(new_center_y)), (0, 0, 255), 8)
                                    annotated_frame = cv2.circle(annotated_frame, (int(center_x), int(center_y)), 5, (0, 255, 0), -1)
                                    annotated_frame =   trace_annotator.annotate(
                                                            annotated_frame, detections=detections)
                                    # update time stamp
                                    self.timestamp +=1
                                    old_center_x = center_x
                                    old_center_y = center_y
                                   
                                result = cv2.add(annotated_frame, canvas)
                                # Display the annotated frame
                                # cv2.imshow("YOLOv8 Tracking", result)
                                result = cv2.resize(result,(600, 300))
                                frame_placeholder.image(result, width=700 ,channels="BGR")
                                # return result
                    
                    # Break the loop if 'q' is pressed
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                    else:
                        continue
                    
                else:
                    print('Confidence less than 60%')    
            else:
                print('No boxes detected')
                break
         # Release the video capture object and close the display window
        cap.release()
        cv2.destroyAllWindows()


def main():
    st.title('Number-plate Tracking')
    
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
        # tracking 
        tracking = Tracking()
        canvas, gray_init_frame = tracking.create_canvas(vid)
        tracking.load_and_process_frames(demo_file,canvas, gray_init_frame)
        st.video(demo_bytes,format="video/mp4")
    
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
    club_tracking = Tracking()
    canvas, gray_init_frame = club_tracking.create_canvas(vid)
    result_frame = club_tracking.load_and_process_frames(vid, canvas, gray_init_frame)
    frame_placeholder.image(result_frame, width=700 ,channels="BGR")
    vid.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass