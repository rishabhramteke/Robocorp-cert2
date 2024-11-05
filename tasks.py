#Import libraries
from robocorp.tasks import task
from robocorp import browser
from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.FileSystem import FileSystem
from RPA.Archive import Archive
import requests
import csv
from io import StringIO

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=1,
    )
    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        pdf_file_path = store_receipt_as_pdf(order["Order number"])
        screenshot_file_path = screenshot_robot(order["Order number"])
        embed_screenshot_to_receipt(screenshot_file_path, pdf_file_path)
        order_another_robot()

def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """Get rid of that annoying modal that pops up when you open the robot order website"""
    page = browser.page()
    page.click("button:text('OK')")

def get_orders():
    """Get the orders from the website"""
    library = Tables()
    csv_data = requests.get("https://robotsparebinindustries.com/orders.csv").text
    csv_reader = csv.DictReader(StringIO(csv_data))
    orders = library.create_table(data=list(csv_reader))
    return orders

def fill_the_form(order):
    """Fill the form with the order data"""
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click("#id-body-" + str(order["Body"]))
    page.fill('input[placeholder="Enter the part number for the legs"]', str(order["Legs"]))
    page.fill("#address", order["Address"])
    page.click("button:text('Preview')")
    while True:
        try:
            page.click("button:text('ORDER')")
            # Wait for receipt to appear to confirm order went through
            page.wait_for_selector("#receipt",timeout=1000)
            break
        except:
            # If order fails, try again
            continue

def store_receipt_as_pdf(order_number):
    """Store the receipt as a pdf file"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_file_path = "output/receipts/" + str(order_number) + ".pdf"
    pdf.html_to_pdf(receipt_html, pdf_file_path)
    return pdf_file_path

def screenshot_robot(order_number):
    """Take a screenshot of the robot"""
    page = browser.page()
    robot_img_html = page.locator("#robot-preview-image")
    screenshot_file_path = "output/robots/" + str(order_number) + ".png"
    robot_img_html.screenshot(path=screenshot_file_path)
    return screenshot_file_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the screenshot to the pdf file"""
    pdf = PDF()
    # Create a list of files to merge: original pdf and screenshot
    # files = [
    #     pdf_file,
    #     screenshot
    # ]
    # # Create a new PDF with both files
    # pdf.add_files_to_pdf(
    #     files=files,
    #     target_document=pdf_file
    # )
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
        source_path=pdf_file,
        output_path=pdf_file
    )

def order_another_robot():
    """Order another robot"""
    page = browser.page()
    page.click("text=Order another robot")

def archive_receipts():
    """Archive the receipts"""
    library = Archive()
    library.archive_folder_with_zip(folder="output/receipts", archive_name="output/receipts.zip")

