import contextlib
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

app = FastAPI()
client = MongoClient('mongodb://localhost:27017')
db = client['courses']


@app.get('/courses')
def get_courses(sort_by: str = 'date', domain: str = None):
    for course in db.courses.find():
        total = 0
        count = 0
        for chapter in course['chapters']:
            with contextlib.suppress(KeyError):
                total += chapter['rating']['total']
                count += chapter['rating']['count']
                db.courses.update_one({'_id': course['_id']}, {'$set': {'rating': {'total': total, 'count': count}}})

        if sort_by == 'date':
            sort_field = 'date'
            sort_order = 1
        elif sort_by == 'rating':
            sort_field = 'rating.total'
            sort_order = 1
        else:
            sort_field = 'name'
            sort_order = 1

        query = {}
        if domain:
            query['domain'] = domain

        courses = db.courses.find(query, {'name': 1, 'date': 1, 'description': 1, 'domain': 1, 'rating': 1, '_id': 0}).sort(sort_field, sort_order)
        courses_list = jsonable_encoder(list(courses))
        return JSONResponse(content=courses_list)

