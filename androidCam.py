import subprocess
import time
import os
import cv2
import sys
import csv

class Android_Recorder():
    def init(self):
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
        
    def Start(self):

        print("\n--> Starting Recording")
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_CAMERA'])

    def Stop(self):
        # Step 3: Stop the video recording
        print('\n--> Recording complete')
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_CAMERA'])

    def Save(self, results_path):

        # Step 4: Wait briefly for the video file to save on the phone
        time.sleep(2)  # Give some time for the file to save properly

        print(f"Closing net.sourceforge.opencamera")
        subprocess.run(['adb', 'shell', 'am', 'force-stop', "net.sourceforge.opencamera"])

        # Step 5: Define the source path on the phone (update as needed)
        if not os.path.exists(results_path):
            os.makedirs(results_path)
        phone_video_dir = "/sdcard/DCIM/OpenCamera/"
        local_video_dir = results_path
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

        self.frame_splitter(local_video_path, (local_video_dir+'/fames'))
        


    # Breaks video into individual frames, saves them, and writes timestamps to a CSV file
    def frame_splitter(self,vid_path, frames_path):
        # Load the video file
        video = cv2.VideoCapture(vid_path)

        csv_path = frames_path+'/timestamps.csv'
        # Create output directory for frames
        if not os.path.exists(frames_path):
            os.makedirs(frames_path)

        frame_count = 0
        first_frame_timestamp = None
        print('\n--> Splitting video into frames\n')

        # Open a CSV file to save timestamps
        with open(csv_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write the header
            csv_writer.writerow(['Frame Number', 'Timestamp (seconds)'])

            while True:
                success, frame = video.read()
                if not success:
                    break

                # Get the actual timestamp of the current frame in milliseconds
                timestamp_ms = video.get(cv2.CAP_PROP_POS_MSEC)

                # On the first frame, store the initial timestamp
                if first_frame_timestamp is None:
                    first_frame_timestamp = timestamp_ms

                # Normalize the timestamp relative to the first frame's timestamp
                normalized_timestamp_ms = timestamp_ms - first_frame_timestamp

                # Convert the timestamp to seconds (with high precision)
                timestamp_seconds = normalized_timestamp_ms / 1000.0

                # Format the timestamp for overlay
                timestamp_str = f"{timestamp_seconds:.5f}"

                # Overlay the timestamp on the frame
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, timestamp_str, (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # Save the frame with timestamp overlay
                frame_filename = f"{frames_path}/frame_{frame_count:04d}.png"
                cv2.imwrite(frame_filename, frame)

                # Write the frame number and timestamp to the CSV file
                csv_writer.writerow([frame_count, timestamp_seconds])

                frame_count += 1

        video.release()
        print(f'\n--> Total frames extracted: {frame_count}\n')
        print(f'--> Timestamps saved to {csv_path}\n')





# if __name__ == '__main__':
#     pass
    # Android_Recorder(results_path="C:/Users/jgver/Documents/University/Thesis/ThesisCode/results")