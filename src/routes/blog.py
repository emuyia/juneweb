from src import app
from src.models import Post, Tag
from flask import render_template, request, flash, jsonify
import requests
import json


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    return render_template("view_post.html", post=post)


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        data = request.get_json()
        if data.get('action') == 'Unsubscribe':
            email_to_unsubscribe = data.get('EMAIL')
            api_key = app.config["MAILCHIMP_API_KEY"]
            list_id = app.config["MAILCHIMP_LIST_ID"]
            server = app.config["MAILCHIMP_DATACENTER"]
            endpoint = f"https://{server}.api.mailchimp.com/3.0/lists/{list_id}/members/{email_to_unsubscribe}"
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            payload = {'status': 'unsubscribed'}
            response = requests.patch(endpoint, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                return jsonify({"message": "Successfully unsubscribed."}), 200
            else:
                return jsonify({"message": "Failed to unsubscribe."}), 400
        else:
            return jsonify({"message": "Invalid action."}), 400
    return render_template('subscribe.html')
