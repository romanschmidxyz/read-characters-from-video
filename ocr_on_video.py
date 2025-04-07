import csv
import google.generativeai as genai
import os
import cv2
from natsort import natsorted, ns
from dotenv import load_dotenv

"""
    Throughout the bomb calorimetry experiment, the students either read the temperature from the calorimeter display every 10 seconds, a process which is straight up tedious, fairly prone to errors and limiting in the number of datapoints collected.
    to prevent such reading errors, videos of the display are recorded and the data is obtained later on. Students then extract datapoints from the video to a data sheet, again, a fairly boring and repetitive endeavor. 

    To remove the need to manually extract the data from the video to a csv file, the following script was designed.



    Step-by-step instructions:
        - Store this file in the SAME FOLDER AS THE VIDEOS

        - Install all the necessary python modules (if you don't have them already):
            google-generativeai
            OpenCV
            natsort
            dotenv
            If you need help or instructions on how to install a module, go ahead and ask google.

        - Generate your API-Key on this website (sign in with your google account): https://aistudio.google.com/app/apikey?hl=de
        - Copy the API-Key
        - In terminal or your code editor, create a new file in the same folder called '.env' and write API_KEY= 'your api key' in the file (The program will then read the key from that file)
        - If you have trouble with the above step, shoot me an E-Mail (attached below) or just put your API-Key directly into the code on line 200: genai.configure(api_key='Your key here')
          and remove the four lines above that.
        - Make sure your internet connection is working fine.
        - Now you're good to go and the program can be executed.

    If executed, the program will:
        - ask you to enter a name for the csv data file. You don't have to put '.csv' at the end. Example: 'data_maleicacid1'
        - ask you to enter the name of the video file that should be processed. Don't forget the video format. Example: 'bombcal_maleicacid1.MP4'
        - extract the frames from the video and store them in a folder called image_frames
        - extract the time and temperature from each frame and add a new row to the csv file. (after character extraction, the frame is deleted)
        - before termination the folder image_frames is deleted automatically and except for the data file no additional hard drive space is consumed.


    The file contains the following methods with respective functionality:
    - files(video_name): takes video name string input, creates folder for frames and fetches the video
    - process(source_vid): takes video file, extracts all the frames and stores them in the frame folder created
    - get_video(): asks user for a valid video name, initiates frame by frame extraction
    - write_to_csv(file_name, row): Creates a csv with the respective filename if it does not exist yet and writes a new row to it. If file_name.csv exists, the row is appended at the bottom.
    - prep_image(path, name): prepares image upload
    - ocr_on_image(image_path, prompt): uses gemini vision model to extract character string from frame
    - character_recognition(path, frame_name): This is a wrapper method. It takes the input (path) from the main caller, delegates file upload and ocr to the respective methods. 
    - def check_format(char_string):checks the format of the extracted character strings
    - get_new_row(character_string): checks the strings and prepares a new row to be added to csv by formatting time in seconds and temperature in °C
    - extract_chars_to_csv(csv_name): loop through the video-frames, extract characters from display, store them in csv file by calling the respective methods mentioned above.

    - MAIN DRIVER METHOD: drives the execution of the process and calls all the necessary methods from above.

    If there are problems/questions text: roman.schmid2@students.unibe.ch

"""

# setup folder for frames and get video
def files(video_name):
    os.makedirs("image_frames")
    source_vid = cv2.VideoCapture(video_name)
    return source_vid
    
    

# extract video frames
def process(source_vid):
    # integer for file names (this enables sorted processing later on)
    name_index = 1
    frame_index = 1
    while source_vid.isOpened():
        ret, frame = source_vid.read()
        # break at the end of the video
        if not ret:
            break

        # save every 150th frame -> video has 30 fps so every 5 seconds a frame is stored
        # adjust this rate according to the video quality and the amount of datapoints needed 
        if frame_index % 150 == 0:
            # name frame and export as png
            name = './image_frames/frame' + str(name_index) + '.png'
            print('Extracting frame ' + name)
            cv2.imwrite(name, frame)
            name_index += 1
        frame_index += 1

    source_vid.release()

# get video information from user and extract its frames into new frame folder using existing methods
def get_video():
    # Asks user for video name. For example: bombcal_calib_benzoicacid1.MP4 
    video_name = input("Please enter a video file name:")
    # make sure it's a valid file name
    while video_name not in os.listdir('.'):
        video_name = input("Please enter a valid file name:")

    # get video file, make frame folder and store frames from video in there
    vid = files(video_name)
    process(vid)

# append data row to csv. If the csv file does not exist yet, it is created automatically
def write_to_csv(file_name, row):
    # create csv file, add labels
    with open(f'{file_name}.csv', 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(row)
        print(row, f" added to {file_name} csv.")


"""
    Methods following handle upload of an image (frame extracted from video) and OCR.
"""

# Uploads file and prints a confirmation
def prep_image(image_path, image_name):
    while True:
        try:
            sample_file = genai.upload_file(path=image_path, display_name=f"{image_name}")
            # exit loop if sample file upload worked
            break
        # if the server is overloaded or there are connection issues, just try again
        except:
            pass

    print(f'Uploaded: {sample_file.display_name} as: {sample_file.uri}')
    file = genai.get_file(name=sample_file.name)
    print(f"Retrieved file {file.display_name} as: {sample_file.uri}")
    return sample_file

# Uses google gemini vision model to do ocr on an image
def ocr_on_image(image_path, prompt):
    # Choose Model, gemini-2.0-flash-lite handles 30 requests per minute
    # Also, it has remarkable OCR performance
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
    while True:
        try:
            response = model.generate_content([image_path, prompt])
            text = response.text
            break
        # if any timeout exception occur (server/connection related stuff) just pass and stay in the loop to retry
        except:
            pass
    return text
    

# This is a wrapper method. It takes the input (path) from the main caller, delegates file upload and ocr to the respective methods.  
def character_recognition(path, frame_name):
    sample_file = prep_image(path, frame_name)
    text = ocr_on_image(sample_file, "Can you extract the characters on the display and return them without anything else?")
    if text:
        print(text)
        return text
    else:
        print(f"Failed to extract text from image {frame_name}.")
        return None
    
# Investigates format of minute and seconds. This allows conversion to int below to calculate total seconds passed.
def check_format(char_string):
    return char_string[-3:].strip().isnumeric() and char_string[-6:-4].isnumeric()

# checks the strings and prepares a new row to be added to csv
def get_new_row(character_string):
    if check_format(character_string):
        # get time in seconds and temp from extracted char string
        time = str(int(character_string[-6:-4])*60 + int(character_string[-3:].strip()))
        temp = character_string.replace(" ", "")[:6]
        if "°" in temp: 
            temp = temp.replace("°", "")
        return [time, temp]
    else:
        return None

# loop through the video-frames, extract characters from display, store them in csv file
def extract_chars_to_csv(csv_name):
    for frame_name in natsorted(os.listdir("image_frames"), alg=ns.IGNORECASE):
        path = "image_frames" + "/" + frame_name
        character_string = character_recognition(path, frame_name)
        if character_string:
            # assert char string has the according format
            row = get_new_row(character_string)
            if row:
                write_to_csv(csv_name, row)
            else:
                print(f"Invalid extracted character format. {frame_name} skipped.")  
        else:
            print(f"No characters extracted from {frame_name}")
        # If some sort of error occurs, removal of the already processed frame allows continuation where the process was interrupted when rerunning.
        os.remove(path)
        



"""
    MAIN DRIVER CODE
"""
if __name__ == '__main__':
    # load .env file (where API_KEY is stored)
    load_dotenv(override=True)
    # access API_KEY as environment variable
    API_KEY = os.getenv("API_KEY")
    # configure google api
    genai.configure(api_key=API_KEY)

    # create csv file to write data into
    file_name = input("Choose a name for the csv file. If the file already exists, the additional data will be appended. Name for CSV: ")
    while file_name == '':
        file_name = input("Stop acting up and just enter a file name (for example: 'data_file'):")

    # if there is no folder for image frames, we need to fetch a video, create frame folder and csv file
    if not os.path.exists("image_frames"):
        get_video()
        label_row = ['Time [s]', 'Temperature [°C]']
        write_to_csv(file_name, label_row)

    # loop through frames and append data to csv
    extract_chars_to_csv(file_name)

    #remove frame directory after completion
    os.rmdir("image_frames")
    print("Finished successfully.")


