**Voter ID Data Extraction Project**


**Overview**
This project aims to extract voter ID details from electronic voter data using OpenCV. By processing scanned download pdfs, we can automatically retrieve relevant information such as name, address, and voter ID number.


**Requirements**
Python 3.x
OpenCV (for image processing)
Tesseract OCR (for text extraction)

**Setup and Usage**
Install the required dependencies:
pip install opencv-python-headless pytesseract


**Clone this repository:**
git clone https://github.com/RagalaSantosh/VoterID

**cd voter_final**

**Run the Batchfile:**
VoterIdExtraction


**How It Works**
Image Preprocessing:
Load the input image.
Apply filters (grayscale, thresholding, etc.) to enhance text visibility.

**Text Extraction:**
Use Tesseract OCR to extract text from the preprocessed image.
Identify relevant fields (name, address, voter ID number).


**Data Parsing:**
Parse the extracted text to retrieve specific details.
Format and display the results.

**Example Output**

Name: Ragala Santosh

Address: 123 Main St, City

Voter ID: ABC123456

**Contributing**
Contributions are welcome! Feel free to open an issue or submit a pull request.
