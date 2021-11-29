from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import darkcyan, darkviolet, purple, red, brown, yellow, blue, black, cyan, ivory, \
    lemonchiffon, mediumspringgreen, lightgrey, grey
import datetime
import json
import sendgrid
import base64
from sendgrid.helpers.mail import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# google sheet creds
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "botpackage/client_secrets.json", scope)
google_client = gspread.authorize(creds)


def generate_diploma(accolade, nickname):
    file = open("botpackage/accolade.json", "r")
    dict_accolade = json.load(file)
    file.close()

    background = dict_accolade[accolade]["background"]
    color = dict_accolade[accolade]["color"]
    title = dict_accolade[accolade]["title"]
    text = dict_accolade[accolade]["text"]
    image = dict_accolade[accolade]["image"]
    width = int(dict_accolade[accolade]["width"])
    height = int(dict_accolade[accolade]["height"])

    time = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
    diploma_name = f"Diploma_{nickname}_{time}.pdf"
    canvas_diploma = Canvas(f"diplomas/{diploma_name}",
                            pagesize=(11 * inch, 8.5 * inch))  # diploma size: 8.5 in x 11 inch

    canvas_diploma.drawImage(f"diplomas/{background}",
                             0, 0, width=11 * inch, height=8.5 * inch)

    canvas_diploma.setFillColor(color)
    canvas_diploma.setStrokeColor(color)
    canvas_diploma.setFont("Courier-Bold", 40)
    canvas_diploma.drawCentredString(11 * inch - 300, 8.5 * inch - 200, title.upper())

    canvas_diploma.setFillColor(black)
    canvas_diploma.setFont("Courier", 15)
    canvas_diploma.drawCentredString(11 * inch - 300, 8.5 * inch - 250, "is presented to")

    canvas_diploma.setFillColor(color)
    canvas_diploma.setFont("Courier-Bold", 30)
    canvas_diploma.drawCentredString(11 * inch - 300, 8.5 * inch - 300, nickname)
    canvas_diploma.setFillColor(color)
    canvas_diploma.setStrokeColor(color)
    canvas_diploma.line(11 * inch - 450, 8.5 * inch - 310, 11 * inch - 150, 8.5 * inch - 310)

    canvas_diploma.setFillColor(black)
    canvas_diploma.setFont("Courier", 15)
    canvas_diploma.drawCentredString(11 * inch - 300, 8.5 * inch - 360, text)

    canvas_diploma.setFont("Courier-BoldOblique", 15)
    canvas_diploma.drawCentredString(11 * inch - 550, 8.5 * inch - 480, "Data:")
    canvas_diploma.setFont("Courier", 15)
    canvas_diploma.drawCentredString(11 * inch - 550, 8.5 * inch - 510, datetime.datetime.now().strftime("%d/%m/%y"))

    canvas_diploma.drawImage(f"diplomas/{image}", 11 * inch - 750,
                             8.5 * inch - 350, width=width, height=height)

    canvas_diploma.drawImage("diplomas/trivia_logo.png", 11 * inch - 300,
                             8.5 * inch - 510, width=65, height=52)
    canvas_diploma.setFillColor(grey)
    canvas_diploma.setFont("Courier-Oblique", 10)
    canvas_diploma.drawCentredString(11 * inch - 210, 8.5 * inch - 510, "by Marinela Vlad")

    canvas_diploma.save()

    return diploma_name


def send_diploma(accolade, email, diploma_name):
    file_emailcontent = open("botpackage/email_content.json", "r")
    dict_email = json.load(file_emailcontent)
    file_emailcontent.close()

    sg_token = open("sendgrid", "r").read()

    sg = sendgrid.SendGridAPIClient(api_key=sg_token)
    from_email = Email("marinelavlad89@gmail.com")
    to_email = To(email)

    mail = Mail(from_email, to_email)

    template_id = dict_email[accolade]["template_id"]
    mail.template_id = template_id

    mail.dynamic_template_data = {
        "subject": dict_email[accolade]["subject"],
        "text1": dict_email[accolade]["content1"],
        "text2": dict_email[accolade]["content2"],
        "text3": dict_email[accolade]["content3"],
    }
    # we attache now the diploma
    file_path = f"diplomas/{diploma_name}"
    data = open(file_path, "rb").read()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('application/pdf')
    attachment.file_name = FileName(dict_email[accolade]["file_name"])
    attachment.disposition = Disposition('attachment')
    mail.attachment = attachment

    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)



def get_email(id):
    auth = google_client.open("TriviaBot").worksheet("auth")
    users_list = auth.col_values(1)
    row = 0
    for i in range(1, len(users_list)):
        if str(id) == str(users_list[i]):
            row = i + 1
            break
    row_id = auth.row_values(row)
    dict = {
        "email": row_id[3],
        "nickname":  row_id[4],
        "premium_player": row_id[5],
        "premium_member": row_id[6],
        "row": row
    }
    return dict

