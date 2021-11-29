import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

#google sheets creds
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "botpackage/client_secrets.json", scope)
google_client = gspread.authorize(creds)

feedback_sheet = google_client.open("TriviaBot").worksheet("feedback")
rating_sheet = google_client.open("TriviaBot").worksheet("rating")


def get_last_feedback(id):
    list_of_lists = feedback_sheet.get_all_values()
    row = 0
    for i in range(len(list_of_lists)-1, 0, -1):
        if str(list_of_lists[i][0]) == str(id):
            row = i
            break
    if row == 0:
        print(f"No review from {id}")
        return "No review"
    else:
        print(f"Last feedback from {id} is:\n{list_of_lists[row]}")
        return list_of_lists[row]



def save_feedback(id, nick, stars, feedback):
    list_of_lists = feedback_sheet.get_all_values()
    row = len(list_of_lists) + 1
    now_date = datetime.datetime.now().strftime("%d/%m/%y %H-%M-%S")
    list_feedback = [str(id), nick, now_date, stars, feedback]
    feedback_sheet.insert_row(list_feedback, row)
    print(f"The feedback was saved in feedback sheet:\n{list_feedback}")
    return list_feedback



def update_rating():
    list_of_lists = feedback_sheet.get_all_values()
    if len(list_of_lists) == 1:
        print("No rating received yet")
        return "No rating received yet"
    else:
        unique_feedback_list = []
        star_sum = 0
        for i in range(len(list_of_lists)-1, 0, -1):
            flag = 0
            for list in unique_feedback_list:
                if list_of_lists[i][0] in list:
                    flag = 1
                    break
            if flag == 0:
                unique_feedback_list.append(list_of_lists[i])
                star_sum += int(list_of_lists[i][3])
        avg_rating = round(float(star_sum/len(unique_feedback_list)), 2)
        dec_avg_rating = avg_rating % 1
        int_avg_rating = int(avg_rating // 1)
        # dec_avg_rating, int_avg_rating = math.modf(avg_rating)   #or this option
        updated_date = datetime.datetime.now().strftime("%d/%m/%y %H-%M-%S")
        no_feedbacks = len(unique_feedback_list)
        no_full_stars = int_avg_rating
        if dec_avg_rating == 0.0:
            no_half_stars = 0
        else:
            no_half_stars = 1
        no_empty_stars = 5 - no_full_stars - no_half_stars
        # UPDATED_DATE	NO_UNIQUE_FEEDBACKS	NO_TOTAL_STARS	AVG_RATING	NO_FULL_STARS	NO_HALF_STARS	NO_EMPTY_STAR
        list_row = [updated_date, no_feedbacks, star_sum, avg_rating, no_full_stars, no_half_stars, no_empty_stars]
        rating_sheet.delete_rows(2,2)
        rating_sheet.insert_row(list_row, 2)
        print(f"Rating sheet was updated at {updated_date}")
        return list_row
