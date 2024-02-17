from src import app
from flask import request, render_template, jsonify
from markupsafe import Markup
import requests

langtable_data = []
langtable_file = "https://raw.githubusercontent.com/emuyia/wd-repackaged/master/nop/whiteday119/data/ini/langtable.wdb"

import re


def load_wdb_file(url):
    response = requests.get(url)
    lines = response.content.decode("euc-kr").split("\n")  # Decode with EUC-KR
    pattern = re.compile(r'"(.*?)"\s*')
    for line in lines:
        matches = pattern.findall(line)
        if len(matches) == 3:
            id, korean, english = matches
            langtable_data.append(
                {"id": id.strip(), "korean": korean.strip(), "english": english.strip()}
            )


def get_langtable_data():
    if not langtable_data:
        load_wdb_file(langtable_file)
    return langtable_data


def get_langtable_item(id):
    data = get_langtable_data()
    return next((item for item in data if item["id"] == id), None)


def replace_special(text):
    text = text.replace("\\n", "<br>")
    text = text.replace("|", "<br>")
    text = text.replace("\\1", "<span style='color: gold;'>")  # Start golden text
    text = text.replace("\\0", "</span>")  # End golden text
    text = text.replace("\\<", "<")
    return text


@app.route("/white-day/langtable-lookup")
def show_langtable():
    search_id = request.args.get("search_id")
    if search_id:
        langtable_item = get_langtable_item(search_id)
        # Apply character replacements if langtable_item is found
        if langtable_item:
            langtable_item["korean"] = Markup(replace_special(langtable_item["korean"]))
            langtable_item["english"] = Markup(
                replace_special(langtable_item["english"])
            )
        return render_template(
            "wd_langtable.html",
            langtable_item=langtable_item,
            langtable_file=langtable_file,
        )
    else:
        return render_template("wd_langtable.html")


@app.route("/langtable/ids")
def langtable_ids():
    ids = [item["id"] for item in langtable_data]
    return jsonify(ids)
