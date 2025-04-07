# read-characters-from-video
Python program that extracts data  from video to a csv file. Designed to quickly make video data accessible for analysis.

Throughout the bomb calorimetry experiment, the students either read the temperature from the calorimeter display every 10 seconds, a process which is straight up tedious, fairly prone to errors and limiting in the number of datapoints collected.
To get around this, videos of the display are recorded. Students then extract datapoints from the video to a data sheet, again, a fairly boring and repetitive endeavor. 
To remove the need to manually extract the data from the video to a csv file, this script was designed.
![Alt text](https://github.com/romanschmidxyz/read-characters-from-video/blob/main/Demo.png)


## Step-by-step instructions
  - Store the 'ocr_on_video.py' file in the SAME FOLDER AS THE VIDEOS
  - Install all the necessary python modules (if you don't have them already):
      - google-generativeai
      - OpenCV
      - natsort
      - dotenv

  - Generate your API-Key on this website (sign in with your google account): https://aistudio.google.com/app/apikey?hl=de
  - Copy the API-Key
  - In terminal or your code editor, create a new file in the same folder called '.env' and write API_KEY='your api key' in the file (The program will then read the key from that file)
    - If you have trouble with the above step, shoot me an E-Mail (attached below) or just put your API-Key directly into the code on line 204: genai.configure(api_key='Your key here') and remove the four lines above that.
  - Make sure your internet connection is working fine.
  - Now you're good to go and the program can be executed.

## If executed, the program will
- ask you to enter a name for the csv data file. You don't have to put '.csv' at the end. Example: 'data_calib_benzoicacid1'
- After pressing enter, it will ask you to enter the name of the video file that should be processed. Don't forget the video format. Example: 'bombcal_calib_benzoicacid1.MP4'
  ![Alt text](https://github.com/romanschmidxyz/read-characters-from-video/blob/main/Step1.png)
- After pressing enter, it will extract the frames from the video and store them in a folder called image_frames
  ![Alt text](https://github.com/romanschmidxyz/read-characters-from-video/blob/main/Frame_extraction.png)
- extract the time and temperature from each frame and add a new row to the csv file. (after character extraction, the frame is deleted)
  ![Alt text](https://github.com/romanschmidxyz/read-characters-from-video/blob/main/Character_recognition_to_csv.png)
- before termination the folder image_frames is deleted automatically and except for the data file no additional hard drive space is consumed.
- If the program is stopped mid process, just run it again. Enter the name of the same csv and the program will resume where it was stopped.

- If there are questions / problems shoot me an E-Mail: roman.schmid2@students.unibe.ch
  or collaborate with me on github.
