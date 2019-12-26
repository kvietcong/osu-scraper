from bs4 import BeautifulSoup
import requests
import json


class OsuProfile:

    # An OsuProfile class retrieves the information of an osu profile and
    # stores it within a json file. That information can then be parsed for
    # specific things like ranking, name, and etc.

    def __init__(self, profile_id):

        # pre: The given identification must be a string and must be a username
        # or a profile id/number. The program is case insensitive
        #
        # post: Initializes an OsuProfile  with the given identification and
        # with the information gathered from the official osu website

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

        # Returns a brief summary of the profile's information

        return f"""Name: {self.get_name()}
Global Rank: {self.get_rank()[0]}
Country Rank: {self.get_rank()[1]}
Total pp: {self.get_pp()}
Playcount: {self.get_play_count()}"""

    def get_name(self):

        # Returns the profile's username

        return self.profile_json["username"]

    def get_user_number(self):

        # Returns the profile's id/number

        return self.profile_json["id"]

    def get_pp(self):

        # Returns the profile's performance points

        return self.profile_json["statistics"]["pp"]

    def get_rank(self):

        # Returns the profile's global and country rank in a list

        return [self.profile_json["statistics"]["rank"]["global"],
                self.profile_json["statistics"]["rank"]["country"]]

    def get_country(self):

        # Returns the profile's country

        return self.profile_json["statistics"]["country"]["name"]

    def get_play_count(self):

        # Returns the profile's play count

        return self.profile_json["statistics"]["play_count"]

    def __str__(self):

        # Returns the profile's full information

        return json_to_string(self.profile_json)

    @staticmethod
    def json_to_string(json_info):

        # Converts the profile's JSON into a string

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


# All the method's below do the same thing as the methods in the
# OsuProfile class but they are calculated independently


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