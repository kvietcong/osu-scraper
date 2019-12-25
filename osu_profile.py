from bs4 import BeautifulSoup
import requests
import json


class OsuProfile:
    def __init__(self, profile_id):
        if type(profile_id) == str:
            self.profile_id = profile_id
            response = requests.get("https://osu.ppy.sh/u/" + self.profile_id)
            web_page_soup = BeautifulSoup(response.text, "html.parser")
            self.profile_json = json.loads(web_page_soup.find(id="json-user")
                                           .getText())
        elif type(profile_id) == json:
            self.profile_json = profile_id
            self.profile_id = self.get_name()

    def get_summary(self):
        return f"""Name: {self.get_name()}
Global Rank: {self.get_rank()[0]}
Country Rank: {self.get_rank()[1]}
Total pp: {self.get_pp()}
Playcount: {self.get_play_count()}"""

    def get_name(self):
        return self.profile_json["username"]

    def get_user_number(self):
        return self.profile_json["id"]

    def get_pp(self):
        return self.profile_json["statistics"]["pp"]

    def get_rank(self):
        return [self.profile_json["statistics"]["rank"]["global"],
                self.profile_json["statistics"]["rank"]["country"]]

    def get_country(self):
        return self.profile_json["statistics"]["country"]["name"]

    def get_play_count(self):
        return self.profile_json["statistics"]["play_count"]

    def __str__(self):
        return json_to_string(self.profile_json)

    @staticmethod
    def json_to_string(json_info):
        tab = " " * 3
        string = ""
        if type(json_info) == dict:
            for key in json_info.keys():
                other = json_to_string(json_info[key])
                other_tabbed = f"\n{tab}".join(other.split("\n"))
                string += f"\n{key}:{tab}{other_tabbed}"
        elif type(json_info) == list:
            for index in range(len(json_info) - 1):
                other = json_to_string(json_info[index])
                other_tabbed = f"\n{tab}".join(other.split("\n"))
                string += f"{other_tabbed}\n"
            if json_info:
                other = json_to_string(json_info[-1])
                other_tabbed = f"\n{tab}".join(other.split("\n"))
                string += f"{other_tabbed}"
            if string == "":
                string += "N/A"
        else:
            string += f"{json_info}"
        return string.replace("_", " ")


def get_profile_json(profile_id):
    response = requests.get("https://osu.ppy.sh/u/" + profile_id)
    web_page_soup = BeautifulSoup(response.text, "html.parser")
    return json.loads(web_page_soup.find(id="json-user").getText())


def json_to_string(profile):
    tab = " " * 3
    string = ""
    if type(profile) == dict:
        for key in profile.keys():
            other = json_to_string(profile[key])
            other_tabbed = f"\n{tab}".join(other.split("\n"))
            string += f"\n{key}:{tab}{other_tabbed}"
    elif type(profile) == list:
        for index in range(len(profile) - 1):
            other = json_to_string(profile[index])
            other_tabbed = f"\n{tab}".join(other.split("\n"))
            string += f"{other_tabbed}\n"
        if profile:
            other = json_to_string(profile[-1])
            other_tabbed = f"\n{tab}".join(other.split("\n"))
            string += f"{other_tabbed}"
        if string == "":
            string += "N/A"
    else:
        string += f"{profile}"
    return string.replace("_", " ")


def get_pp(profile_id):
    return get_profile_json(profile_id)["statistics"]["pp"]


def get_rank(profile_id):
    return [get_profile_json(profile_id)["statistics"]["rank"]["global"],
            get_profile_json(profile_id)["statistics"]["rank"]["country"]]


def get_country(profile_id):
    return get_profile_json(profile_id)["country"]["name"]


def get_play_count(profile_id):
    return get_profile_json(profile_id)["statistics"]["play_count"]