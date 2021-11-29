from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import darkcyan, darkviolet, purple, red, brown, yellow, blue, black, cyan, ivory, \
    lemonchiffon, mediumspringgreen, lightgrey, grey
from .diplomas import *
from .boards import *
import datetime
import sendgrid
import base64
from sendgrid.helpers.mail import *

# google sheets creds
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "botpackage/client_secrets.json", scope)
google_client = gspread.authorize(creds)

transactions_bot = google_client.open("TriviaBot").worksheet("transactions")


def create_account(id, amount):
    # transactions_bot = google_client.open("TriviaBot").worksheet("transactions")
    id_accounts_list = transactions_bot.col_values(1)
    row = len(id_accounts_list) + 1

    transactions_bot.insert_row(
        [str(id), datetime.datetime.now().strftime("%d/%m/%y"), "Open account", amount, 0, amount], row)
    print("The account has been created!")
    return id


def check_balance(id):
    # transactions_bot = google_client.open("TriviaBot").worksheet("transactions")
    id_accounts_list = transactions_bot.col_values(1)
    # I look for the last transaction  and return the balance from there
    for i in range(1, len(id_accounts_list)):
        if str(id_accounts_list[i]) == str(id):
            row = i + 1
    try:
        return float((transactions_bot.cell(row, 6).value).replace(",", ""))
    except UnboundLocalError:
        return "No bank account"


def donate(from_id, to_id, amount, details):
    # transactions_bot = google_client.open("TriviaBot").worksheet("transactions")
    id_accounts_list = transactions_bot.col_values(1)
    row = len(id_accounts_list) + 1
    from_id_balance = check_balance(from_id)
    to_id_balance = check_balance(to_id)
    transactions_bot.insert_row(
        [str(from_id), datetime.datetime.now().strftime("%d/%m/%y"), f"Transfer to {to_id} ({details})", 0, amount,
         float(from_id_balance) - float(amount)], row)
    row += 1
    transactions_bot.insert_row(
        [str(to_id), datetime.datetime.now().strftime("%d/%m/%y"), f"Transfer from {from_id} ({details})", amount, 0,
         float(to_id_balance) + float(amount)], row)

    print("Both transactions are done!")
    return (from_id, to_id)


def refund_account(id, amount):
    # transactions_bot = google_client.open("TriviaBot").worksheet("transactions")
    id_accounts_list = transactions_bot.col_values(1)
    row = len(id_accounts_list) + 1
    id_balance = check_balance(id)
    transactions_bot.insert_row(
        [str(id), datetime.datetime.now().strftime("%d/%m/%y"), f"Refund the account", amount, 0,
         float(id_balance + amount)], row)
    return id


def ads_remuneration(amount):
    id = '848949680809574460'
    # transactions_bot = google_client.open("TriviaBot").worksheet("transactions")
    id_accounts_list = transactions_bot.col_values(1)
    row = len(id_accounts_list) + 1
    id_balance = check_balance(id)
    transactions_bot.insert_row(
        [str(id), datetime.datetime.now().strftime("%d/%m/%y"), f"Remuneration from ads", amount, 0,
         float(id_balance + amount)], row)
    return id


def server_account_report(server_id):
    list_of_transactions = transactions_bot.get_all_values()
    total_sold = check_balance(server_id)
    no_transactions = 0
    sold_from_premium_member = 0
    no_transactions_premium_member = 0
    sold_from_donation_to_server = 0
    no_transactions_donation_to_server = 0
    sold_from_ads = 0
    no_transactions_ads = 0
    for list_row in list_of_transactions[1:]:
        if str(list_row[0]) == str(server_id):
            no_transactions += 1
            if "Premium Member Title" in list_row[2]:
                sold_from_premium_member += float(list_row[3])
                no_transactions_premium_member += 1
            elif "(Donation to Server)" in list_row[2]:
                sold_from_donation_to_server += float(list_row[3])
                no_transactions_donation_to_server += 1
            elif "Remuneration from ads" in list_row[2]:
                sold_from_ads += float(list_row[3])
                no_transactions_ads += 1
    return (no_transactions, total_sold, no_transactions_premium_member, sold_from_premium_member,
            no_transactions_donation_to_server, sold_from_donation_to_server, no_transactions_ads, sold_from_ads)


# Generates account statements via email
def generate_account_statements_pdf(id):
    time_now = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
    file_name = f"Account_statements{id}_{time_now}.pdf"
    canvas_file = Canvas(f"account_statements/{file_name}",
                         pagesize=(8.33 * inch, 11.7 * inch))
    background = "account_statement_background.png"
    canvas_file.drawImage(f"account_statements/{background}",
                          0, 0, width=8.33 * inch, height=11.7 * inch)

    red_color = "0xA82D2D"

    ### we create the antet first:
    canvas_file.setFont("Courier-Bold", 12)
    canvas_file.setFillColor(red_color)

    dict = get_email(id)
    canvas_file.drawString(50, 780, f"Member_id: {id}")
    canvas_file.drawString(50, 760, f"Nickname: {dict['nickname']}")
    canvas_file.drawString(50, 740, f"Email: {dict['email']}")
    canvas_file.drawString(50, 720, f"Server: TriviaBot")
    canvas_file.drawString(50, 700, f"Currency: RON(lei)")
    canvas_file.drawString(50, 50, f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")

    # then we create the table antet
    canvas_file.setStrokeColor(lightgrey)
    canvas_file.line(50, 670, 8.33 * inch - 50, 670)

    canvas_file.setFillColor(black)
    canvas_file.drawString(50, 650, "DATA")
    canvas_file.drawString(120, 650, "TRANSACTION DETAILS")
    canvas_file.drawString(340, 650, "CREDIT(+)")
    canvas_file.drawString(420, 650, "DEBIT(-)")
    canvas_file.drawString(500, 650, "SOLD")

    canvas_file.setStrokeColor(lightgrey)
    canvas_file.line(50, 640, 8.33 * inch - 50, 640)

    # now I put in pdf every transaction associated to the given id
    canvas_file.setFillColor(black)
    canvas_file.setFont("Courier", 10)

    # transactions_bot = google_client.open("TriviaBot").worksheet("transactions")
    id_accounts_list = transactions_bot.col_values(1)
    y = 620
    for i in range(1, len(id_accounts_list)):
        if str(id_accounts_list[i]) == str(id):
            row = i + 1
            info = transactions_bot.row_values(row)
            data = str(info[1]).rstrip()
            details = str(info[2]).rstrip()
            credit = str(info[3]).rstrip()
            debit = str(info[4]).rstrip()
            sold = str(info[5]).rstrip()
            # there are trans details with long len that have details in '('
            if "(" not in details:
                canvas_file.drawString(50, y, f"{data}")
                canvas_file.drawString(120, y, f"{details}")
                canvas_file.drawString(340, y, f"{credit}")
                canvas_file.drawString(420, y, f"{debit}")
                canvas_file.drawString(500, y, f"{sold}")
            else:
                canvas_file.drawString(50, y, f"{data}")
                canvas_file.drawString(120, y, f"{details.split(' (')[0]}")
                canvas_file.drawString(340, y, f"{credit}")
                canvas_file.drawString(420, y, f"{debit}")
                canvas_file.drawString(500, y, f"{sold}")
                y -= 20
                canvas_file.drawString(120, y, f"({details.split(' (')[1]}")
            y -= 20

    canvas_file.setStrokeColor(lightgrey)
    canvas_file.line(50, y, 8.33 * inch - 50, y)

    canvas_file.drawImage("diplomas/trivia_logo.png", 8.33 * inch - 150,
                          50, width=65, height=52)
    canvas_file.setFillColor(red_color)
    canvas_file.setFont("Courier-Oblique", 8)
    canvas_file.drawCentredString(8.33 * inch - 70, 40, "by Marinela Vlad")

    canvas_file.save()

    return file_name



def send_account_statements(nickname, email, file_name):
    sg_token = open("sendgrid", "r").read()

    sg = sendgrid.SendGridAPIClient(api_key=sg_token)
    from_email = Email("marinelavlad89@gmail.com")
    to_email = To(email)
    subject = "Your account statement from TriviaBot Server"
    text = f"""Hello {nickname},

Please find attached your account statement from TriviaBot Server.

We hope you enjoy our server!

Yours,
TriviaBot team"""
    content = Content("text/plain", text)
    mail = Mail(from_email, to_email, subject, content)

    file_path = f"account_statements/{file_name}"
    data = open(file_path, "rb").read()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('application/pdf')
    # attachment.file_type = FileType('image/png')
    attachment.file_name = FileName("Your_account_statement.pdf")
    attachment.disposition = Disposition('attachment')
    mail.attachment = attachment

    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    return response.status_code




def about_myself(id):
    myself_dict = get_email(id)

    # about account
    # transactions_bot = google_client.open("TriviaBot").worksheet("transactions")
    id_accounts_list = transactions_bot.col_values(1)
    if check_balance(id) != "No bank account":
        myself_dict['account_id'] = id
    else:
        myself_dict['account_id'] = "No bank account yet"
    if check_balance(id) != "No bank account":
        myself_dict['sold'] = check_balance(id)
    else:
        myself_dict['sold'] = 'N/A'
    data_account = 'N/A'
    if check_balance(id) != "No bank account":
        row = 1
        for i in range(1, len(id_accounts_list)):
            if str(id_accounts_list[i]) == str(id):
                row = i + 1
                break
        data_account = transactions_bot.cell(row, 2).value
    myself_dict['data_account'] = data_account

    no_transactions = 'N/A'
    if check_balance(id) != "No bank account":
        no_transactions = 0
        for i in range(1, len(id_accounts_list)):
            if str(id_accounts_list[i]) == str(id):
                no_transactions += 1
    myself_dict['no_transactions'] = no_transactions

    # info about game:
    scoring_sheet = google_client.open("TriviaBot").worksheet("scoring")
    ids_list = scoring_sheet.col_values(1)
    if str(id) in ids_list:
        myself_dict['player_id'] = id
    else:
        myself_dict['player_id'] = "You play no game yet"

    no_sessions = len(scoring_dict[str(id)].keys())
    total_time = 0
    total_q = 0
    total_score = 0
    for session in scoring_dict[str(id)].keys():
        total_time += scoring_dict[str(id)][session][0]
        total_q += scoring_dict[str(id)][session][1]
        total_score += scoring_dict[str(id)][session][2]

    myself_dict['no_sessions'] = no_sessions
    myself_dict['total_time'] = total_time
    myself_dict['total_no_questions'] = total_q
    myself_dict['total_score'] = total_score

    leaderboards()
    sheet_leaderboard = google_client.open("TriviaBot").worksheet("leaderboards")
    leaders_list = sheet_leaderboard.col_values(1)

    if str(id) in leaders_list:
        for i in range(1, len(leaders_list)):
            if str(leaders_list[i]) == str(id):
                row = i + 1
                break
        myself_dict['leaderboard_place'] = row - 1
    else:
        myself_dict['leaderboard_place'] = 'N/A'

    return myself_dict


