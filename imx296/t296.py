import cv2
from picamera2 import Picamera2

def live_camera_view():
    # Create a Picamera2 object
    picam2 = Picamera2()

    # Set up video configuration
    config = picam2.create_video_configuration()
    picam2.configure(config)

    # Start the camera
    picam2.start()

    print("Live camera feed started. Press 'q' to exit.")

    try:
        while True:
            # Capture an image (in numpy array format)
            frame = picam2.capture_array()

            # Convert the image to BGR format (the format used by OpenCV)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Display the image on the screen
            cv2.imshow('Live Camera Feed', frame_bgr)

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
