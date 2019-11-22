import models
from flask import jsonify, Blueprint, request
from flask_login import login_required, current_user
from playhouse.shortcuts import model_to_dict

review = Blueprint('reviews', 'review')


@review.route('/', methods=['POST'])
@login_required
def post_review():
    try:
        payload = request.get_json()
        review = models.Review.create(**payload, user_id=current_user.id)
        review_dict = model_to_dict(review)
        review_dict['user_id'].pop('password')
        return jsonify(
            data=review_dict,
            status={
                "code": 201,
                "message": "Review submitted and accepted."
            }
        ), 201
    except models.IntegrityError:
        return jsonify(
            data={},
            status={
                "code": 422,
                "message": "No media matches the provided media_id."
            }
        ), 422


@review.route('/<revId>', methods=['PUT'])
@login_required
def update_review(revId):
    payload = request.get_json()
    print(payload)
    try:
        review = models.Review.get_by_id(revId)
        if model_to_dict(review.user_id)['id'] == current_user.id:
            review.rating = payload['rating'] if payload['rating'] else None
            review.body = payload['body'] if payload['body'] else None
            review.save()
            return jsonify(
                data=model_to_dict(review),
                status={
                    "code": 200,
                    "message": "Review successfully updated."
                }
            )
    except models.DoesNotExist:
        return jsonify(
            data={},
            status={
                "code": 422,
                "message": "No review matches the provided media_id."
            }
        ), 422
    else:
        return jsonify(
            data={},
            status={
                "code": 403,
                "message": "That's not your review."
            }
        ), 403
