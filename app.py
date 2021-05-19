# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import ArtistForm, VenueForm, ShowForm
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database
from models import *


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    record = []
    try:
        venues = Venue.query.distinct(Venue.city, Venue.state).all()
        if venues:
            for venue in venues:
                upcoming_shows = len(Venue.query.join(Shows)
                                     .filter(Shows.c.start_time > datetime.utcnow(),
                                             Shows.c.venue_id == venue.id).all())
                data = []
                for i in Venue.query.filter_by(city=venue.city, state=venue.state).all():
                    print(i)
                    data.append({"id": i.id, "name": i.name, "num_upcoming_shows": upcoming_shows})
                record.append({"city": venue.city, "state": venue.state, "venues": data})
    except Exception as e:
        print(e)
    return render_template("pages/venues.html", areas=record)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")
    search_response = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    records = []
    for venue in search_response:
        records.append({"id": venue.id, "name": venue.name,
                        "num_upcoming_shows": len(Venue.query.join(Shows).filter(Shows.c.start_time > datetime.utcnow(),
                                                                                 Shows.c.venue_id == venue.id).all())
                        })
    response = {"count": len(search_response), "data": records}
    return render_template("pages/search_venues.html", results=response,
                           search_term=request.form.get("search_term", ""))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    try:
        venue_f = Venue.query.filter_by(id=venue_id).first()
        #list_shows = db.session.query(Shows).filter(Shows.c.venue_id == venue_f.id).all()
        #print(venue_f, list_shows)
        records = {}
        list_shows = db.session.query(Shows).join(Venue).filter(Shows.c.venue_id==venue_f.id)
        artist_up_show = []
        artist_past_show = []
        for show in list_shows:
            artist = Artist.query.filter_by(id=show.artist_id).first()
            start_time = format_datetime(str(show.start_time))
            artist_show = {"artist_id": artist.id, "artist_name": artist.name, "artist_image_link": artist.image_link,
                           "start_time": start_time}
            if show.start_time >= datetime.utcnow():
                artist_up_show.append(artist_show)
            elif show.start_time < datetime.utcnow():
                artist_past_show.append(artist_show)
        records = {"id": venue_f.id, "name": venue_f.name, "genres": venue_f.genres, "address": venue_f.address,
                   "city": venue_f.city, "state": venue_f.state, "phone": venue_f.phone,
                   "website": venue_f.website_link,
                   "facebook_link": venue_f.facebook_link, "seeking_talent": venue_f.seeking_talent,
                   "seeking_description": venue_f.seeking_description, "image_link": venue_f.image_link,
                   "upcoming_shows": artist_up_show, "upcoming_shows_count": len(artist_up_show),
                   "past_shows": artist_past_show, "past_shows_count": len(artist_past_show)}
    except Exception as e:
        pass
    return render_template("pages/show_venue.html", venue=records)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    venue_data = {}
    venue_form = VenueForm()
    venue_data['name'] = venue_form.name.data
    venue_data['phone'] = venue_form.phone.data
    venue_data['address'] = venue_form.address.data
    venue_data['city'] = venue_form.city.data
    venue_data['image_url'] = venue_form.image_link.data
    venue_data['facebook_url'] = venue_form.facebook_link.data
    venue_data['state'] = venue_form.state.data
    venue_data['genres'] = venue_form.genres.data
    venue_data['seeking_talent'] = venue_form.seeking_talent.data
    venue_data['seeking_description'] = venue_form.seeking_description.data
    venue_data['website'] = venue_form.website_link.data

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    venue = Venue(name=venue_data.get('name'), city=venue_data.get('city'), state=venue_data.get('state'),
                  address=venue_data.get('address'), phone=venue_data.get('phone'),
                  image_link=venue_data.get('image_url'),
                  facebook_link=venue_data.get('facebook_url'), genres=venue_data.get('genres'),
                  website_link=venue_data.get('website'), seeking_talent=venue_data.get('seeking_talent'),
                  seeking_description=venue_data.get('seeking_description'))
    try:
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + venue_data.get('name') + " was successfully listed!")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Venue " +
              venue_data.get('name') + " could not be listed.")
        db.session.flush()
        print(e)
    return render_template("pages/home.html")


@app.route('/venues/<venue_id>/delete', methods=['POST', 'GET', 'DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    venue = Venue.query.filter_by(id=venue_id).first()

    db.session.delete(venue)
    db.session.commit()
    flash('Record Deleted Successfully')

    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists', methods=['GET'])
def artists():
    # TODO: replace with real data returned from querying the database
    all_artist = []
    try:
        all_artist = Artist.query.all()
    except Exception as e:
        db.session.rollback()
        db.session.close()
    data = []
    if all_artist:
        for artist in all_artist:
            data.append({"id": artist.id, "name": artist.name})
    return render_template("pages/artists.html", artists=all_artist)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term", "")
    search_response = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    data = []
    for artist in search_response:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(Artist.query.join(Shows).
                                      filter(Shows.c.start_time > datetime.now(), Shows.c.artist_id == artist.id).all())
        })

    response = {
        "count": len(search_response),
        "data": data
    }
    return render_template("pages/search_artists.html", results=response,
                           search_term=request.form.get("search_term", ""))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    shows = db.session.query(Shows).filter(Shows.c.artist_id == artist_id).all()
    venue_past_shows = []
    venue_up_shows = []
    artist = Artist.query.filter_by(id=artist_id).first()
    data = None

    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        start_time = format_datetime(str(show.start_time))

        venue_show = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(start_time)
        }
        if show.start_time >= datetime.utcnow():
            venue_up_shows.append(venue_show)
        elif show.start_time < datetime.utcnow():
            venue_past_shows.append(venue_show)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "website": artist.website_link,
        "image_link": artist.image_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "upcoming_shows_count": len(venue_up_shows),
        "upcoming_shows": venue_up_shows,
        "past_shows": venue_past_shows,
        "past_shows_count": len(venue_past_shows),

    }
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()

    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html",
                           form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website_link = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    db.session.merge(artist)
    db.session.commit()
    flash("Record Updated Successfully!")
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(id=venue_id)
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.get(id=venue_id)

    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.address = form.address.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data

    db.session.merge(venue)
    db.session.commit()
    flash("Record Updated Successfully!")
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    artist_form = ArtistForm()
    name = artist_form.name.data
    phone = artist_form.phone.data
    city = artist_form.city.data
    image_url = artist_form.image_link.data
    facebook_url = artist_form.facebook_link.data
    state = artist_form.state.data
    genres = artist_form.genres.data
    website = artist_form.website_link.data
    seeking_venue = artist_form.seeking_venue.data
    seeking_description = artist_form.seeking_description.data
    artist = Artist(name=name, city=city, state=state, phone=phone,
                    website_link=website, genres=genres, image_link=image_url,
                    facebook_link=facebook_url, seeking_venue=seeking_venue,
                    seeking_description=seeking_description)
    # TODO: modify data to be the data object returned from db insertion(DONE)
    try:
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + artist.name + " was successfully listed!")
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        flash("An error occurred. Artist " +
              artist.name + " could not be listed.")
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        print(e)
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    all_shows = []
    try:
        venues_all = Venue.query.join(Artist, Venue.state == Artist.state).all()
        data = db.session.query(Shows).all()
        for show in data:
            artist = Artist.query.filter_by(id=show.artist_id).first()
            venue = Venue.query.filter_by(id=show.venue_id).first()
            all_shows.append({
                "venue_id": show.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time
            })
    except Exception as e:
        print(e)
        pass

    return render_template("pages/shows.html", shows=all_shows)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    show_form = ShowForm()
    artist_id = show_form.artist_id.data
    venue_id = show_form.venue_id.data
    start_time = show_form.start_time.data

    show = Shows.insert().values(artist_id=artist_id,
                                 venue_id=venue_id, start_time=start_time)
    try:
        db.session.execute(show)
        db.session.commit()
        flash("Show was successfully listed!")
    except Exception as e:
        flash("An error occurred. Show could not be listed.")
        db.session.rollback()
        db.session.flush()
        print(e)
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
