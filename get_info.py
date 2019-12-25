import json
import tkinter
from tkinter import filedialog
import os.path
from osu_profile import OsuProfile
from bs4 import BeautifulSoup
import requests
import sys


def get_top_stats(page_stop=1):
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


def get_rank_player(rank):
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
    return OsuProfile(player)


def get_players(players):
    print("Proceeding to retrieve data")
    osu_profiles = {}
    progress = 0.0
    sys.stdout.write(f"\n{progress}%")
    for username in players:
        osu_profiles[username] = get_player(username)
        progress += 1 / len(players) * 100
        formatted_progress = format(progress, ".2f")
        sys.stdout.write(f"\r{formatted_progress}%")

    sys.stdout.write(f"\r{formatted_progress}%, Data Retrieved\n")
    return osu_profiles


def print_players(players, print_stats, write_json=False, save_stats=False,
                  file_name="default", file_directory=""):
    result = {} if write_json else ""
    if type(players) == dict:
        for username, profile in players.items():
            if not write_json:
                result += f"\n{profile.get_summary()}\n"
            else:
                result[username] = profile.profile_json
    elif type(players) == list:
        for index in range(len(players)):
            if not write_json:
                result += f"\n{players[index].get_summary()}\n"
            else:
                result[players[index].get_name(),
                       players[index].profile_json]
    else:
        if not write_json:
            result += players.get_summary()
        else:
            result = players.profile_json

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
    print("\nPick a File Destination")
    print("Close the window to save it in the project path")
    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    return filedialog.askdirectory()


def two_option_input(prompt, choices):
    while True:
        user_input = input(f"{prompt}\n")
        if user_input == choices[0]:
            return True
        elif user_input == choices[1]:
            return False


def is_integer(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def run_scraper():
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
        profiles = get_top_stats(page)
    else:
        names = input_players.split(",")
        for index in range(len(names)):
            names[index] = names[index].strip()
        profiles = get_players(names)

    write_json = two_option_input(
        "Would you like a summary or a JSON? (s/j)",
        ["f", "s"])
    print_stats = two_option_input(
        "Would you like to print the stats? (y/n)",
        ["y", "n"])
    save_stats = two_option_input(
        "Would you like to save the stats? (y/n)",
         ["y", "n"])

    if save_stats:
        print_players(profiles, print_stats, write_json, save_stats,
                      input("What would you like the file to be named?\n"),
                      get_file_path())
    else:
        print_players(profiles, print_stats, write_json)
