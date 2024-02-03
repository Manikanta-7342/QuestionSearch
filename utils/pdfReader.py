# To read the PDF
import PyPDF2, time
# To analyze the PDF layout and extract text
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


def pdf_extract(pdf_path):
    text = ""
    start = time.time()
    # Create a pdf file object
    if type(pdf_path) == str:
        pdfFileObj = open(pdf_path, 'rb')
    else:
        pdfFileObj = pdf_path
    # Create a pdf reader object
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)

    # Create the dictionary to extract text from each image
    text_per_page = {}

    # We extract the pages from the PDF
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        page_content = []

        # Find all the elements
        page_elements = [(element.y1, element) for element in page._objs]
        # Sort all the element as they appear in the page 
        page_elements.sort(key=lambda a: a[0], reverse=True)


        # Find the elements that composed a page
        for i,component in enumerate(page_elements):
            # Extract the element of the page layout
            element = component[1]

            # Check if the element is text element
            if isinstance(element, LTTextContainer):
                # Use the function to extract the text and format for each text element
                line_text = element.get_text()
                page_content.append(line_text)


        text = text  + "\n" + ''.join(page_content)

    # Close the pdf file object
    pdfFileObj.close()
    end = time.time()
    print(f"Time used to extract a pdf is {end-start}")
    return text

if __name__ == '__main__':
    pdf_path = "YOUR_PDF_FILE_PATH"
    text = pdf_extract(pdf_path)
    with open('wordsFrequency.txt','w') as file:
        file.write(text)
    
