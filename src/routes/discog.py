from src import app, db
from src.models import Album, Track
from src.routes.auth import admin_required

from flask import render_template, request, redirect, url_for
from datetime import datetime


@app.route('/discog')
def discog():
    albums = Album.query.order_by(Album.release_date).all()
    return render_template('discog.html', albums=albums)


@app.route("/album/<int:album_id>")
def view_album(album_id):
    album = Album.query.get(album_id)

    dt = datetime.strptime(album.release_date, "%Y%m%d")
    formatted_release_date = dt.strftime("%d-%m-%Y")

    return render_template("view_album.html", album=album, release_date=formatted_release_date)


@app.template_filter('todict')
def to_dict(track):
    return {
        'id': track.id,
        'name': track.name,
        'duration': track.duration
    }


@app.route("/add_album", methods=["GET", "POST"])
@app.route("/edit_album/<int:album_id>", methods=["GET", "POST"])
@admin_required
def manage_album(album_id=None):
    album = None
    if album_id:
        album = Album.query.get(album_id)
    if request.method in ["POST", "PUT"]:
        title = request.form["title"]
        artist = request.form["artist"]
        release_date = request.form["release_date"]
        cover_image = request.form["cover_image"]
        embed = request.form["embed"]
        content = request.form["content"]

        if album:
            album.name = title
            album.artist = artist
            album.release_date = release_date
            album.cover_image = cover_image
            album.embed = embed
            album.content = content
        else:
            album = Album(title=title,
                          artist=artist,
                          release_date=release_date,
                          cover_image=cover_image,
                          embed=embed,
                          content=content)
            db.session.add(album)

        track_ids = request.form.getlist('tracks[][id]')
        track_names = request.form.getlist('tracks[][name]')
        track_durations = request.form.getlist('tracks[][duration]')
        submitted_track_ids = set(int(track_id) for track_id in track_ids if track_id)
        db_track_ids = set(track.id for track in album.tracks)
        deleted_track_ids = db_track_ids - submitted_track_ids

        for track_id in deleted_track_ids:
            Track.query.filter_by(id=track_id).delete()

        for track_id, track_name, track_duration in zip(track_ids, track_names, track_durations):
            if track_id:
                track = Track.query.get(int(track_id))
                track.name = track_name
                track.duration = track_duration
            else:
                track = Track(name=track_name, duration=track_duration)
                album.tracks.append(track)

        db.session.commit()
        return redirect(url_for("blog"))
    return render_template("manage_album.html", album=album)
