# To read the PDF
import PyPDF2
# To analyze the PDF layout and extract text
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer
# To extract text from tables in PDF
import pdfplumber
# To extract the images from the PDFs
from PIL import Image
from pdf2image import convert_from_path
# To perform OCR to extract text from images 
import pytesseract 
# To remove the additional created files
import os
import sys


# Create function to extract text
def text_extraction(element):
    # Extracting the text from the in line text element
    line_text = element.get_text()
    
    # Return a text in each line 
    return line_text

# Extracting tables from the page

def extract_table(pdf_path, page_num, table_num):
    # Open the pdf file
    pdf = pdfplumber.open(pdf_path)
    # Find the examined page
    table_page = pdf.pages[page_num]
    # Extract the appropriate table
    table = table_page.extract_tables()[table_num]
    
    return table

# Convert table into appropriate fromat
def table_converter(table):
    table_string = ''
    # Iterate through each row of the table
    for row_num in range(len(table)):
        row = table[row_num]
        # Remove the line breaker from the wrapted texts
        cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
        # Convert the table into a string 
        table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
    # Removing the last line break
    table_string = table_string[:-1]
    return table_string

# Create a function to check if the element is in any tables present in the page
def is_element_inside_any_table(element, page ,tables):
    x0, y0up, x1, y1up = element.bbox
    # Change the cordinates because the pdfminer counts from the botton to top of the page
    y0 = page.bbox[3] - y1up
    y1 = page.bbox[3] - y0up
    for table in tables:
        tx0, ty0, tx1, ty1 = table.bbox
        if tx0 <= x0 <= x1 <= tx1 and ty0 <= y0 <= y1 <= ty1:
            return True
    return False

# Function to find the table for a given element
def find_table_for_element(element, page ,tables):
    x0, y0up, x1, y1up = element.bbox
    # Change the cordinates because the pdfminer counts from the botton to top of the page
    y0 = page.bbox[3] - y1up
    y1 = page.bbox[3] - y0up
    for i, table in enumerate(tables):
        tx0, ty0, tx1, ty1 = table.bbox
        if tx0 <= x0 <= x1 <= tx1 and ty0 <= y0 <= y1 <= ty1:
            return i  # Return the index of the table
    return None  


def pdf_extract(pdf_path):
    text = ""
    # Create a pdf file object
    if type(pdf_path) == str:
        pdfFileObj = open(pdf_path, 'rb')
    else:
        pdfFileObj = pdf
    # Create a pdf reader object
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)

    # Create the dictionary to extract text from each image
    text_per_page = {}

    # We extract the pages from the PDF
    for pagenum, page in enumerate(extract_pages(pdf_path)):

        # Initialize the variables needed for the text extraction from the page
        pageObj = pdfReaded.pages[pagenum]
        text_from_tables = []
        page_content = []
        # Initialize the number of the examined tables
        table_in_page= -1
        # Open the pdf file
        pdf = pdfplumber.open(pdf_path)
        # Find the examined page
        page_tables = pdf.pages[pagenum]
        # Find the number of tables in the page
        tables = page_tables.find_tables()
        if len(tables)!=0:
            table_in_page = 0

        # Extracting the tables of the page
        for table_num in range(len(tables)):
            # Extract the information of the table
            table = extract_table(pdf_path, pagenum, table_num)
            # Convert the table information in structured string format
            table_string = table_converter(table)
            # Append the table string into a list
            text_from_tables.append(table_string)

        # Find all the elements
        page_elements = [(element.y1, element) for element in page._objs]
        # Sort all the element as they appear in the page 
        page_elements.sort(key=lambda a: a[0], reverse=True)


        # Find the elements that composed a page
        for i,component in enumerate(page_elements):
            # Extract the element of the page layout
            element = component[1]

            # Check the elements for tables
            if table_in_page == -1:
                pass
            else:
                if is_element_inside_any_table(element, page ,tables):
                    table_found = find_table_for_element(element,page ,tables)
                    if table_found == table_in_page and table_found != None:    
                        page_content.append(text_from_tables[table_in_page])
                        table_in_page+=1
                    # Pass this iteration because the content of this element was extracted from the tables
                    continue

            if not is_element_inside_any_table(element,page,tables):

                # Check if the element is text element
                if isinstance(element, LTTextContainer):
                    # Use the function to extract the text and format for each text element
                    line_text = text_extraction(element)
                    page_content.append(line_text)


        text = text + "\n" + ''.join(text_from_tables) + "\n" + ''.join(page_content)

        # Create the key of the dictionary
        dctkey = 'Page_'+str(pagenum)
        # Add the list of list as value of the page key
        text_per_page[dctkey]= [text_from_tables, page_content]

    # Close the pdf file object
    pdfFileObj.close()

    return (text_per_page,text)

if __name__ == '__main__':
    pdf_path = sys.argv[1]
    text_per_page, text = pdf_extract(pdf_path)
    with open('wordsFrequency.txt','w') as file:
        file.write(text)
    # Display the content of the page
    # print(f"All content is \n {text}")
    # result = ''.join(text_per_page['Page_46'][4])
    # print(result)
