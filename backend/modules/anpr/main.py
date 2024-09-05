import re
import cv2
from PIL import Image

from modules.anpr.google_ocr import read_image

def formatLicense(input_string):
    # Regular expression pattern to match "AD" or "DU"
    pattern = r'(AD|DU)'

    matches = re.findall(pattern, input_string)

    if matches:
        match = input_string.find(matches[0])
        return input_string[match:match+5]
        return desired_text
    else:
        return None

def read_license_plate(img_pth):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """
    text = read_image(img_pth)

    license_txt = formatLicense(text.upper().replace(' ', ''))

    print("TXT:", text.upper().replace(' ', ''),"\nLIC:", license_txt)

    return license_txt

def ANPR(image:str):

    # read frames
    ret = True
    count = 0

    frame = cv2.imread(image)

    # # process license plate
    # license_plate_crop_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # # Resize the image
    # resized_plate = cv2.resize(license_plate_crop_gray, (0, 0), fx=6, fy=6, interpolation=cv2.INTER_LANCZOS4)

    # # Binarize using custom thresholding
    # _, thresholded_plate = cv2.threshold(resized_plate, 155, 255, cv2.THRESH_BINARY)

    # license_plate_crop_gray = thresholded_plate

    cv2.imwrite("test.png", frame)

    count+=1

    # read license plate number
    license_plate_text = read_license_plate("test.png")

    if license_plate_text is not None:
        return license_plate_text
    return 0