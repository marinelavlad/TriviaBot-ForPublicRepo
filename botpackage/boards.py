import gspread
from oauth2client.service_account import ServiceAccountCredentials

#google sheets creds
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "botpackage/client_secrets.json", scope)
google_client = gspread.authorize(creds)

scoring_bot = google_client.open("TriviaBot").worksheet("scoring")
boards_bot = google_client.open("TriviaBot").worksheet("leaderboards")

list_of_lists = scoring_bot.get_all_values()

# we create the scoring dict
scoring_dict = {}
for i in range(1, len(list_of_lists)):
    if list_of_lists[i][0] not in scoring_dict.keys():
        scoring_dict[f"{list_of_lists[i][0]}"] = {}
    scoring_dict[f"{list_of_lists[i][0]}"][f"{list_of_lists[i][1]}"] = [
        int(list_of_lists[i][2]),
        int(list_of_lists[i][3]),
        int(list_of_lists[i][4])]

def leaderboards():
    # then we clear all the rows of the leaderboard
    users_list = boards_bot.col_values(1)
    boards_bot.delete_rows(2, len(users_list))

    # then we create an up-to-date leaderboards

    row = 1
    for nickname in scoring_dict.keys():
        row += 1
        total_sessions = len(scoring_dict[nickname].keys())
        total_time = 0
        total_no_questions = 0
        total_score = 0
        for session in scoring_dict[nickname].keys():
            total_time += scoring_dict[nickname][session][0]
            total_no_questions += scoring_dict[nickname][session][1]
            total_score += scoring_dict[nickname][session][2]
        correct_answer_rate = round(float(total_score/total_no_questions)*100, 2)

        boards_bot.insert_row([nickname, total_sessions, total_time, total_no_questions, total_score, correct_answer_rate], row)

    # Sort range A2:G8 basing on column 'G' A -> Z
    # and column 'B' Z -> A
    index = f"A2:F{len(boards_bot.col_values(1))}"
    boards_bot.sort((5, 'des'), (6, 'des'), range=index)
    print(f"Leaderboard successfully updated in google spread sheets!")



def total_score(id):

    total_score = 0
    for session in scoring_dict[str(id)].keys():
        total_score += int(scoring_dict[str(id)][session][2])
    return total_score