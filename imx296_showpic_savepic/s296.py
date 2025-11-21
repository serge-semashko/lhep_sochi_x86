import cv2
from picamera2 import Picamera2
import time
from os import environ
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print(' python-dotenv not installed, rely on environment variable')

def live_camera_view():
    # Create a Picamera2 object
    picam2 = Picamera2()

    # Set up video configuration
    print(environ.get("GAIN"), environ.get("EXPOSURE_TIME"))
    picam2_gain = float(environ.get("GAIN"))
    picam2_ExposureTime = int(environ.get("EXPOSURE_TIME"))

    config = picam2.create_video_configuration()
    controls = {'ExposureTime': picam2_ExposureTime, 'AnalogueGain': picam2_gain, 'FrameRate': 40}
    config = picam2.create_still_configuration(controls=controls)

    picam2.configure(config)

    # Start the camera
    picam2.start()

    print("Live camera feed started. Press 'q' to exit.")

    try:
        while True:
            # Capture an image (in numpy array format)
            frame = picam2.capture_array()
            frame = cv2.resize(frame,None,fx=0.5,fy=0.5)
            # Convert the image to BGR format (the format used by OpenCV)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Display the image on the screen
            cv2.imshow('Live Camera Feed', frame_bgr)
            tm = time.gmtime()
            if not os.path.exists('images'):
                os.makedirs('images')    
            file_name ='images/'+ str(tm.tm_mon) + '-' + str(tm.tm_mday) + '_' + str(tm.tm_hour) + '-' + str(tm.tm_min) + '-'+str(tm.tm_sec) + '.png'

            cv2.imwrite(file_name, frame)


            # Exit the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        # When the user wants to exit with Ctrl+C
        print("\nProgram is terminating...")

    finally:
        # Stop the camera and close OpenCV windows
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    live_camera_view()
