import models
from flask import jsonify, Blueprint, request
from flask_login import login_required, current_user
from playhouse.shortcuts import model_to_dict

viewership = Blueprint('viewership', 'viewership')


@viewership.route('/', methods=['POST'])
@login_required
def add_to_library():
    payload = request.get_json()
    try:
        viewership = models.Viewership.get_or_create(
            user_id=current_user.id,
            media_id=payload['media_id']
        )
        return jsonify(
            data={
                "viewership": model_to_dict(viewership[0])
            },
            status={
                "code": 201,
                "message": "Got resource"
            }
        ), 201
    except models.DoesNotExist:
        return jsonify(
            data={},
            status={
                "code": 422,
                "message": "Can't find the media you're referencing."
            }
        ), 422


@viewership.route('/', methods=['GET'])
@login_required
def show_own_library():
    q = (models.Media
         .select()
         .join(models.Viewership)
         .join(models.User)
         .where(models.User.id == current_user.id))
    media_list = [model_to_dict(m) for m in q.execute()]
    return jsonify(
        data=media_list,
        status={
            "code": 200,
            "message": "Got all titles."
        }
    )


@viewership.route('/<userId>', methods=['GET'])
@login_required
def show_other_library(userId):
    q = (models.Media
         .select()
         .join(models.Viewership)
         .join(models.User)
         .where(models.User.id == userId))
    media_list = [model_to_dict(m) for m in q.execute()]
    return jsonify(
        data=media_list,
        status={
            "code": 200,
            "message": "Got all their titles."
        }
    )


@viewership.route('/<mediaId>', methods=['DELETE'])
@login_required
def remove_from_library(mediaId):
    try:
        q = (models.Viewership
             .select()
             .where((models.Viewership.user_id == current_user.id) &
                    (models.Viewership.media_id == mediaId)))
        viewership = q.execute()
        print(viewership[0])
        viewership[0].delete_instance()
        return jsonify(
            data={},
            status={
                "code": 204,
                "message": "Successfully removed {} from your library."
            }
        ), 204
    except (models.DoesNotExist, IndexError):
        return jsonify(
            data={},
            status={
                "code": 422,
                "message": "Couldn't find that entry."
            }
        ), 422
