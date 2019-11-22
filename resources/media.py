import models
from flask import jsonify, request, Blueprint
from playhouse.shortcuts import model_to_dict, fn

media = Blueprint('media', 'media')


@media.route('/', methods=['GET'])
def index():
    try:
        media_list = [model_to_dict(m) for m in models.Media.select()]
        return jsonify(
            data=media_list,
            status={
                "code": 200,
                "message": "Got all media. *evil laugh*"
            }
        )
    except Exception:
        return jsonify(
            data={},
            status={
                "code": 500,
                "message": "It looks like something went wrong. Our bad."
            }
        ), 500


@media.route('/', methods=['POST'])
def add_item():
    payload = request.get_json()
    try:
        models.Media.get(models.Media.external_id == payload['external_id'])
    except models.DoesNotExist:
        try:
            new_media = models.Media.create(**payload)
        except models.IntegrityError:
            return jsonify(
                data={},
                status={
                    "code": 422,
                    "message": "Cannot process media from before 1906, after 2020."
                }
            ), 422
        else:
            new_media_dict = model_to_dict(new_media)
            return jsonify(
                data=new_media_dict,
                status={
                    "code": 201,
                    "message": "Successfully added media item"
                }
            ), 201
    else:
        return jsonify(
            data={},
            status={
                "code": 422,
                "message": "Cannot add duplicate media item."
            }
        ), 422


@media.route('/<id>', methods=['GET'])
def show(id):
    try:
        media = models.Media.get_by_id(id)
        media_list = model_to_dict(media)
        reviews = []
        for r in media.reviews:
            reviews.append(model_to_dict(r))

        def strip_extra(review):
            print(review)
            review.pop('media_id')
            review['user_id'].pop('password')
            return review
        media_list['reviews'] = list(map(strip_extra, reviews))
        return jsonify(
            data=media_list,
            status={
                "code": 200,
                "status": "Found requested item."
            }
        )
    except models.DoesNotExist:
        return jsonify(
            data={},
            status={
                "code": 404,
                "message": "Couldn't locate that media item."
            }
        ), 404


@media.route('/latest', methods=['GET'])
def index_with_reviews():
    try:
        # this is some complex peewee that seems to get the job done
        # http://docs.peewee-orm.com/en/latest/peewee/relationships.html#subqueries
        # allegedly, this will be the inner query?
        Latest = models.Review.alias()
        lq = (Latest
              .select(Latest.media_id, fn.MAX(Latest.date_added).alias('max_date'))
              .group_by(Latest.media_id)
              .alias('lq'))
        # this is to match both media id and the latest from the subq above
        pred = ((models.Review.media_id == lq.c.media_id) &
                (models.Review.date_added == lq.c.max_date))
        # the final outer query 
        q = (models.Review
             .select(models.Review, models.Media.external_id)
             .join(lq, on=pred)
             .join_from(models.Review, models.Media))
        maybe = [model_to_dict(m) for m in q.execute()]
        print(maybe)
        return jsonify(
            data=maybe,
            status={
                "code": 200,
                "message": "Got all media. *evil laugh*"
            }
        )
    except Exception:
        return jsonify(
            data={},
            status={
                "code": 500,
                "message": "It looks like something went wrong. Our bad."
            }
        ), 500
