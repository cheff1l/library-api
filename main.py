from flask import Flask
from flask_restful import Api
from flasgger import Swagger

from api.books import BookListResource, BookResource


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.update(
        RESTFUL_JSON={"ensure_ascii": False},
        SWAGGER={
            "title": "Library API",
            "uiversion": 3,
        },
    )
    if test_config:
        app.config.update(test_config)

    app.url_map.strict_slashes = False

    Swagger(
        app,
        template={
            "swagger": "2.0",
            "info": {
                "title": "Library API",
                "description": "REST API для керування книгами бібліотеки на Flask-RESTful.",
                "version": "4.0.0",
            },
            "basePath": "/",
            "tags": [{"name": "Books", "description": "Операції з книгами"}],
        },
    )

    api = Api(app)
    api.add_resource(BookListResource, "/books")
    api.add_resource(BookResource, "/books/<string:book_id>")

    @app.get("/")
    def root():
        return {
            "message": "Library API is running!",
            "swagger": "/apidocs/",
            "endpoints": ["/books", "/books/<id>"],
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
