import re
import cv2
from PIL import Image

import easyocr
reader = easyocr.Reader(['en'])

def formatLicense(input_string):
    # Regular expression pattern to match "AD" or "DB"
    pattern = r'(AD|DB)'

    matches = re.findall(pattern, input_string)

    if matches:
        match = input_string.find(matches[0])
        return input_string[match:match+5]
        return desired_text
    else:
        return None

def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """
    text = " ".join(reader.readtext(license_plate_crop, detail = 0))
    
    license_txt = formatLicense(text.upper().replace(' ', ''))

    print("TXT:", text.upper().replace(' ', ''),"\nLIC:", license_txt)

    return license_txt, 0  # Confidence score not available in pytesseract

def ANPR(image:str):

    # read frames
    ret = True
    count = 0

    frame = cv2.imread(image)

    # process license plate
    license_plate_crop_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Resize the image
    resized_plate = cv2.resize(license_plate_crop_gray, (0, 0), fx=6, fy=6, interpolation=cv2.INTER_LANCZOS4)

    # Binarize using custom thresholding
    _, thresholded_plate = cv2.threshold(resized_plate, 155, 255, cv2.THRESH_BINARY)

    license_plate_crop_gray = thresholded_plate

    cv2.imwrite("test.png", license_plate_crop_gray)

    count+=1

    # Convert numpy array to PIL Image
    # license_plate_pil_image = Image.fromarray(license_plate_crop_gray)

    # read license plate number
    license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_gray)

    if license_plate_text is not None:
        return license_plate_text
    return 0

