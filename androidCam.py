import subprocess
import time
import os
import cv2
import sys


def main():

    # Run 'adb devices' to check if any device is connected
    connectionCheck = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    
    # Parse the output to see if there are any connected devices
    devices = connectionCheck.stdout.strip().splitlines()
    
    # The second line onwards should contain device information
    if len(devices) <= 1 or "device" not in devices[1]:
        raise Exception("No device connected. Please connect a device and try again.")

    # Step 1: Start Open Camera and begin recording
    try:
    
        subprocess.run(['adb', 'shell', 'am', 'start', '-n', 'net.sourceforge.opencamera/.MainActivity'])
        time.sleep(1) #Allow camera to autofocus

    #If the subprocess fails then the camera hasn't connected properly, so exit program
    except subprocess.CalledProcessError as e:
        # If the command fails, print an error message and stop the program
        print(f"Camera connection error: {e}")
        sys.exit(1)  # Exit the program with an error status

    # except Exception as e:
    #     # Handle other exceptions, such as no device detected
    #     print(f"Error: {e}")
    #     sys.exit(1)  # Exit the program with an error status

    print("\n--> Starting Recording")
    subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_CAMERA'])

    # Step 2: Wait for the desired recording duration (adjust this duration)
    time.sleep(1)  # Adjust this time to how long you want to record

    # Step 3: Stop the video recording
    print('\n--> Recording complete')
    subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_CAMERA'])

    # Step 4: Wait briefly for the video file to save
    time.sleep(2)  # Give some time for the file to save properly

    # Step 5: Define the source path on the phone (update as needed)
    phone_video_dir = "/sdcard/DCIM/OpenCamera/"
    local_video_dir = "C:/Users/jgver/Documents/University/Thesis/ThesisCode/results"  # Update this to your local directory
    video_filename = "VID_"  # You may need to update this to match the file format of the camera app

    # Step 6: Use ADB to list the files and pull the latest video
    result = subprocess.run(['adb', 'shell', 'ls', '-t', phone_video_dir], capture_output=True, text=True)
    files = result.stdout.splitlines()

    # Find the most recent video file
    for file in files:
        if file.startswith(video_filename) and file.endswith(".mp4"):
            latest_video = file
            break

    # Step 7: Pull the video file from phone to PC
    phone_video_path = os.path.join(phone_video_dir, latest_video)
    local_video_path = os.path.join(local_video_dir, latest_video)

    subprocess.run(['adb', 'pull', phone_video_path, local_video_path])

    # Step 8 (Optional): Confirm the transfer was successful
    if os.path.exists(local_video_path):
        print(f"--> Video successfully transferred to {local_video_path}")
    else:
        print("Video transfer failed.")

    frame_splitter(local_video_path, (local_video_dir+'/fames'))
    




#Breaks video into individual frames and saves them
def frame_splitter(vid_path, frames_path):
    # Load the video file
    video = cv2.VideoCapture(vid_path)

    # Get frames per second (fps) of the video
    fps = video.get(cv2.CAP_PROP_FPS)

    # Create output directory for frames
    if not os.path.exists(frames_path):
        os.makedirs(frames_path)

    frame_count = 0
    print('\n--> Splitting video into frames\n')
    while True:
        success, frame = video.read()
        if not success:
            break

        # Calculate the timestamp for the frame
        timestamp = frame_count / fps
        timestamp_str = f"{int(timestamp // 3600):02}:{int((timestamp % 3600) // 60):02}:{timestamp % 60:.2f}"

        # Overlay timestamp on the frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, timestamp_str, (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Save the frame with timestamp
        frame_filename = f"{frames_path}/frame_{frame_count:04d}.png"
        cv2.imwrite(frame_filename, frame)

        frame_count += 1

    video.release()



if __name__ == '__main__':
    main()