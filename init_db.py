from app import app, db, Album, Track, BlogPost, User, datetime


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin_user = User(username="june",
                          password="***REMOVED***",
                          is_admin=True)

        album = Album(title="Example",
                      artist="Example",
                      release_date="20200101",
                      cover_image="https://images2.imgbox.com/34/2a/c6hF2yJh_o.jpg",
                      content="Example")
        track = Track(name="Track 1",
                      duration="3:45")
        album.tracks.append(track)

        post = BlogPost(title="Example",
                        content="Example",
                        date_posted=datetime.now(),
                        date_updated=datetime.now(),
                        author="example")

        db.session.add(admin_user)
        db.session.add(album)
        db.session.add(post)

        db.session.commit()


init_db()
