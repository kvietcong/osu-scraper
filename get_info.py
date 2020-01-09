import json
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os.path
from osu_profile import OsuProfile
from bs4 import BeautifulSoup
import requests
import concurrent.futures


def get_top_stats(page_stop=1):

    # pre: The given page must be less than 200 and greater than
    # 1 or else another page will be calculated.
    #
    # post: Returns a dictionary of the osu profiles on each page
    # (that the user specified) listed by username.

    if page_stop > 200:
        print("Cannot calculate past the 200th page")
        print("Proceeding to calculate up to the 200th page")
        page_stop = 200
    if page_stop < 1:
        print("Cannot calculate before the 1st page")
        print("Proceeding to calculate the 1st page")
        page_stop = 1

    print("Proceeding to retrieve data")
    osu_ranking_pages = {}
    osu_profiles = {}
    progress = 0.0
    sys.stdout.write(f"\n{progress}%")

    for page_number in range(1, page_stop + 1):
        url = f"https://osu.ppy.sh/rankings/osu/performance?page=" \
              f"{page_number}#scores"
        response = requests.get(url)
        osu_ranking_pages[page_number] = \
            BeautifulSoup(response.text, "html.parser")

    for ranking_page in osu_ranking_pages:
        users = osu_ranking_pages[ranking_page].\
            find_all(class_="ranking-page-table__user-link-text js-usercard")
        for user in users:
            username = user.text.strip()
            osu_profiles[username] = OsuProfile(username)
            progress += 1 / len(users) / len(osu_ranking_pages) * 100
            formatted_progress = format(progress, ".2f")
            sys.stdout.write(f"\r{formatted_progress}%")

    sys.stdout.write(f"\r{formatted_progress}%, Process Completed\n")
    return osu_profiles


def get_top_stats_threaded(page_stop=1, max_threads=2):

    # pre: The given page must be less than 200 and greater than
    # 1 or else another page will be calculated. This function is
    # able to use multithreading to make the task faster. However,
    # be careful of request timeouts as osu blocks out this program
    # if to many requests are made at the same time. (429 error)
    #
    # post: Returns a dictionary of the osu profiles on each page
    # (that the user specified) listed by username.

    if page_stop > 200:
        print("Cannot calculate past the 200th page")
        print("Proceeding to calculate up to the 200th page")
        page_stop = 200
    if page_stop < 1:
        print("Cannot calculate before the 1st page")
        print("Proceeding to calculate the 1st page")
        page_stop = 1

    print("Proceeding to retrieve data")
    osu_ranking_pages = {}
    osu_profiles = {}

    for page_number in range(1, page_stop + 1):
        url = f"https://osu.ppy.sh/rankings/osu/performance?page=" \
              f"{page_number}#scores"
        response = requests.get(url)
        osu_ranking_pages[page_number] = \
            BeautifulSoup(response.text, "html.parser")

    for ranking_page in osu_ranking_pages:
        users = osu_ranking_pages[ranking_page].\
            find_all(class_="ranking-page-table__user-link-text js-usercard")

        users = map(get_username, users)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            profiles = executor.map(get_player, users)

        for profile in profiles:
            osu_profiles[profile.get_name()] = profile

    return osu_profiles


def get_username(user):
    return user.text.strip()


def get_rank_player(rank):

    # pre: The given rank must be below 10001 and above 0 or else
    # None is returned.
    #
    # post: Returns the osu profile of the given rank based on the
    # leader-board.

    if rank > 10000:
        print("Can't find ranks above 10,000")
        return None
    if rank < 1:
        print("Can't find ranks below 1")
        return None

    page_stop = int(rank / 50)
    index_on_page = (rank % 50 - 1) if (rank % 50 != 0) else 49
    if rank % 50:
        page_stop += 1

    response = requests.get(f"https://osu.ppy.sh/rankings/osu/"
                            f"performance?page={page_stop}#scores")
    osu_page = BeautifulSoup(response.text, "html.parser")

    users = osu_page.\
        find_all(class_="ranking-page-table__user-link-text js-usercard")
    username = users[index_on_page].text.strip()

    return OsuProfile(username)


def get_player(player):

    # pre: The string should be a username or player id with the identifier
    # being case insensitive.
    #
    # post: Returns osu profile of the player.
    print(f"Getting {player}")
    return OsuProfile(player)


def get_players(profile_ids):

    # pre: The list should have usernames or player ids with the identifier
    # being case insensitive.
    #
    # post: Returns a dictionary of the osu profiles of each user given
    # listed by username.

    print("Proceeding to retrieve data")
    osu_profiles = {}
    progress = 0.0
    sys.stdout.write(f"\n{progress}%")
    for profile_id in profile_ids:
        player = get_player(profile_id)
        osu_profiles[player.get_name()] = player
        progress += 1 / len(profile_ids) * 100
        formatted_progress = format(progress, ".2f")
        sys.stdout.write(f"\r{formatted_progress}%")

    sys.stdout.write(f"\r{formatted_progress}%, Data Retrieved\n")
    return osu_profiles


def record_stats(players, print_stats, write_json=False, save_stats=False,
                 file_name="default", file_directory=""):

    # pre: The players must be of string type and the print_stats must be a
    # boolean.
    #
    # post: Records the stats of the given players into the console and/or a
    # file. Depending on the user the file is a .txt or a .json.

    result = {} if write_json else ""
    if type(players) == str:
        if not write_json:
            result = f"\n{players.get_summary()}\n"
        else:
            result = players.profile_json
    else:
        players = players.items() if type(players) == dict \
            else enumerate(players)
        for key, profile in players:
            if not write_json:
                result += f"\n{profile.get_summary()}\n"
            else:
                result[profile.get_name()] = profile.profile_json

    if print_stats:
        if write_json:
            print(json.dumps(result, indent=2))
        else:
            print(result)
    if save_stats:
        extension = ".json" if write_json else ".txt"
        save_to = os.path.join(file_directory, f"{file_name}{extension}")
        with open(save_to, "w", encoding="utf-8") as file:
            if write_json:
                json.dump(result, file, indent=2)
            else:
                file.write(result)


def get_file_path():

    # Uses Tkinter GUI to ask for a file destination.

    print("\nPick a File Destination")
    print("Close the window to save it in the project path")
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    return filedialog.askdirectory()


def bool_two_option_input(prompt, choices):

    # pre: The prompt must be a string and there must only be
    # two choices in the choices input. The first choice corresponds
    # with True while the second, false.
    #
    # post: Returns a boolean based on the player's input.

    print(f"{prompt}")
    while True:
        user_input = input()
        if user_input == choices[0]:
            return True
        elif user_input == choices[1]:
            return False
        print("Didn't Quite Understand that :(")


def is_integer(string):

    # Checks if the given String is an integer.

    try:
        int(string)
        return True
    except ValueError:
        return False


def run_scraper_text():

    # Runs a console based script that allows for a client to scrape
    # osu profile information.

    print("Welcome to Le osu! Data Scraper")
    input_players = input(
        "Please list the players you would like to get data of."
        " (Comma separated please!)\n"
        'You can also type "top" to calculate top players\n')
    if "top" in input_players:
        print("What page would you like to go to?"
              " (Each page contains 50)")
        while True:
            user_input = input()
            if is_integer(user_input):
                page = int(user_input)
                break
            print("Didn't Quite Understand that :(")
        profiles = get_top_stats_threaded(page)
    else:
        names = input_players.split(",")
        for index in range(len(names)):
            names[index] = names[index].strip()
        profiles = get_players(names)

    write_json = bool_two_option_input(
        "Would you like a summary or a JSON? (s/j)",
        ["j", "s"])
    print_stats = bool_two_option_input(
        "Would you like to print the stats? (y/n)",
        ["y", "n"])
    save_stats = bool_two_option_input(
        "Would you like to save the stats? (y/n)",
        ["y", "n"])

    if save_stats:
        record_stats(profiles, print_stats, write_json, save_stats,
                     input("What would you like the file to be named?\n"),
                     get_file_path())
    else:
        record_stats(profiles, print_stats, write_json)


# GUI still work in progress
def run_scraper_gui():
    # Starts a new instance of tkinter
    app = Tk()
    app.geometry("600x300")
    app.title("osu! Scraper")

    # Welcome message
    intro = Label(app, text="Welcome to Le osu! Data Scraper!")
    intro.place(relx=.5, rely=.1, anchor="center")

    # File Type chooser
    type_label = Label(app, text="What type would you like the file to be printed in?")
    type_label.place(relx=.4, rely=.2, anchor="center")
    data_type_combobox = ttk.Combobox(app)
    data_type_combobox["values"] = ["Summary", "JSON"]
    data_type_combobox.current(0)
    data_type_combobox.place(relx=.75, rely=.2, anchor="center")

    # Print prompt
    print_checkbox_state = BooleanVar()
    print_checkbox_state.set(True)
    print_checkbox = Checkbutton(app, text="Print Data?", var=print_checkbox_state)
    print_checkbox.place(relx=.225, rely=.3, anchor="center")

    # Save prompt
    save_checkbox_state = BooleanVar()
    save_checkbox_state.set(False)
    save_checkbox = Checkbutton(app, text="Save Data?", var=save_checkbox_state)
    save_checkbox.place(relx=.375, rely=.3, anchor="center")

    # File Name chooser
    file_name_label = Label(app, text="File Name")
    file_name_label.place(relx=.55, rely=.3, anchor="center")
    file_name_input = Entry(app, width=25)
    file_name_input.place(relx=.735, rely=.3, anchor="center")

    # Name input
    players_label = Label(app, text="Names (comma separated)")
    players_label.place(relx=.15, rely=.4, anchor="center")
    players_input = Entry(app, width=65)
    players_input.place(relx=.625, rely=.4, anchor="center")

    def process():

        # Retrieves information put into GUI and fetches the data

        write_json = True if data_type_combobox.get() == "JSON" else False
        save_stats = save_checkbox_state.get()
        file_name = file_name_input.get()
        print_stats = print_checkbox_state.get()

        names = players_input.get().split(",")
        for index in range(len(names)):
            names[index] = names[index].strip()
        players = get_players(names)

        file_pathway = ""
        if save_stats:
            file_pathway = get_file_path()
        if file_name == "":
            file_name = "default"

        record_stats(players,
                     print_stats,
                     write_json=write_json,
                     save_stats=save_stats,
                     file_name=file_name,
                     file_directory=file_pathway)

    # Button to start fetching data
    button = Button(app, text="Fetch Data", command=process)
    button.place(relx=.5, rely=.9, anchor="center")
    app.mainloop()
