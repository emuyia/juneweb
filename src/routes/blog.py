from src import app
from src.models import Post
from flask import render_template, request, flash, redirect, url_for
import requests


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    return render_template("view_post.html", post=post)


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    api_key = app.config['MAIL_API_KEY']
    headers = {
        'Content-Type': 'application/json',
        'X-MailerLite-ApiKey': api_key,
    }
    if request.method == 'POST':
        email = request.form['email']
        if 'unsubscribe' in request.form:
            # Unsubscribe Logic
            response = requests.get(f'https://api.mailerlite.com/api/v2/subscribers/{email}', headers=headers)
            if response.status_code == 200:
                subscriber_id = response.json()['id']
                group_id = app.config['MAIL_GROUP_ID']
                response = requests.delete(f'https://api.mailerlite.com/api/v2/groups/{group_id}/subscribers/{subscriber_id}', headers=headers)
                if response.status_code == 200 or response.status_code == 204:
                    flash('Unsubscribed successfully')
                    return redirect(url_for('subscribe'))
                else:
                    flash('Error unsubscribing')
                    print(f"Unsubscribe failed with status {response.status_code}: {response.content}")
            else:
                flash('Error finding subscriber')
                print(f"Subscriber retrieval failed with status {response.status_code}: {response.content}")
        elif 'subscribe' in request.form:
            # Subscribe Logic
            group_id = app.config['MAIL_GROUP_ID']
            response = requests.post(f'https://api.mailerlite.com/api/v2/groups/{group_id}/subscribers', headers=headers, json={'email': email})
            if response.status_code == 200:
                flash('Subscribed successfully')
                return redirect(url_for('subscribe'))
            else:
                flash('Error subscribing')
                print(f"Subscribe failed with status {response.status_code}: {response.content}")
    return render_template('subscribe.html')
