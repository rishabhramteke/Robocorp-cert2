*** Settings ***
Library    RPA.Browser.Playwright
Library    RPA.Tables
Library    RPA.HTTP
Library    RPA.PDF
Library    RPA.FileSystem
Library    RPA.Archive

*** Variables ***
${URL}    https://robotsparebinindustries.com/#/robot-order
${ORDERS_URL}    https://robotsparebinindustries.com/orders.csv
${OUTPUT_DIR}    ${CURDIR}/output/
${RECEIPT_DIR}    ${OUTPUT_DIR}receipts/
${ROBOT_DIR}    ${OUTPUT_DIR}robots/

*** Tasks ***
Order Robots From RobotSpareBin
    [Documentation]    Orders robots from RobotSpareBin Industries Inc., saves receipts and screenshots, and archives them.
    Create Output Directories
    New Page    ${URL}
    @{orders}    Get Orders
    FOR    ${order}    IN    @{orders}
        Close Annoying Modal
        Fill The Form    ${order}
        ${pdf_file_path}    Store Receipt As PDF    ${order}[Order number]
        ${screenshot_file_path}    Screenshot Robot    ${order}[Order number]
        Embed Screenshot To Receipt    ${screenshot_file_path}    ${pdf_file_path}
        Order Another Robot
    END
    Archive Receipts

*** Keywords ***
Create Output Directories
    Create Directory    ${OUTPUT_DIR}
    Create Directory    ${RECEIPT_DIR}
    Create Directory    ${ROBOT_DIR}

Close Annoying Modal
    Click    button:text("OK")

Get Orders
    RPA.HTTP.Download    ${ORDERS_URL}    overwrite=True
    ${table}=    Read Table From Csv    orders.csv
    [Return]    ${table}

Fill The Form
    [Arguments]    ${order}
    Select Options By    //select[@id='head']    value    ${order}[Head]
    Click    //input[@id='id-body-${order['Body']}']
    Fill Text    //input[@placeholder="Enter the part number for the legs"]    ${order}[Legs]
    Fill Text    //input[@id='address']    ${order}[Address]
    Click    button:text("Preview")
    Wait For Elements State    button:text("ORDER")
    WHILE    True
        Click    button:text("ORDER")
        ${receipt_visible}=    Run Keyword And Return Status    Wait For Elements State    //div[@id='receipt']    visible    timeout=1s
        Run Keyword If    ${receipt_visible}    Exit For Loop
        Sleep    1s
    END

Store Receipt As PDF
    [Arguments]    ${order_number}
    ${receipt_html}=    Get Property    //div[@id='receipt']    innerHTML
    ${pdf_file_path}=    Set Variable    ${RECEIPT_DIR}${order_number}.pdf
    Html To PDF    ${receipt_html}    ${pdf_file_path}
    [Return]    ${pdf_file_path}

Screenshot Robot
    [Arguments]    ${order_number}
    ${screenshot_file_path}=    Set Variable    ${ROBOT_DIR}${order_number}.png
    Take Screenshot    selector=//div[@id='robot-preview-image']    filename=${screenshot_file_path}
    [Return]    ${screenshot_file_path}

Embed Screenshot To Receipt
    [Arguments]    ${screenshot}    ${pdf_file}
    Add Watermark Image To PDF    ${screenshot}    ${pdf_file}    ${pdf_file}

Order Another Robot
    Click    text=Order another robot

Archive Receipts
    Archive Folder With ZIP    folder=${RECEIPT_DIR}    archive_name=${OUTPUT_DIR}receipts.zip
