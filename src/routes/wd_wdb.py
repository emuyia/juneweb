from src import app
from flask import request, render_template, jsonify
from markupsafe import Markup
import requests
import re

langtable_data = []
langtable_file = "https://raw.githubusercontent.com/emuyia/wd-repackaged/master/nop/whiteday119/data/ini/langtable.wdb"


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
    text = text.replace("\\1", "<span style='color: gold;'>")
    text = text.replace("{", "<span style='color: gold;'>")
    text = text.replace("\\0", "</span>")
    text = text.replace("}", "</span>")
    text = text.replace("\\<", "<")
    return Markup(text)


def process_langtable_search(search_id):
    langtable_item = get_langtable_item(search_id)
    if langtable_item:
        langtable_item["korean"] = replace_special(langtable_item["korean"])
        langtable_item["english"] = replace_special(langtable_item["english"])
    return langtable_item


@app.route("/white-day/langtable/ids")
def langtable_ids():
    ids = [item["id"] for item in langtable_data]
    return jsonify(ids)


def natural_keys(text):
    """
    Splits the input text into a list of strings and integers,
    allowing natural sorting (i.e., "2" comes before "10").
    """
    return [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", text)]


def get_documents():
    data = get_langtable_data()
    documents = []
    for entry in data:
        if entry["id"].startswith("d_"):
            _, number = entry["id"].split("_")
            if int(number) % 2 == 1:  # Odd numbers are titles
                documents.append(
                    {
                        "title_en": replace_special(entry["english"]),
                        "title_ko": replace_special(entry["korean"]),
                        "content_en": "",
                        "content_ko": "",
                        "id": entry["id"],
                    }
                )
            else:  # Even numbers are contents
                if documents:  # Check if there's at least one document
                    documents[-1]["content_en"] = replace_special(entry["english"])
                    documents[-1]["content_ko"] = replace_special(entry["korean"])
    documents.sort(key=lambda doc: natural_keys(doc["title_en"]))
    return documents
