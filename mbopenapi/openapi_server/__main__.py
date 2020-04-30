#!/usr/bin/env python3

import connexion

from openapi_server import encoder
from flask_cors import CORS


def mbapi():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'MetricsBuilder API'},
                pythonic_params=True)
    CORS(app.app)
    # app.run(port=8080, ssl_context=('cert.pem', 'key.pem'))
    # app.run()
    return app


# if __name__ == '__main__':
#     mbapi = mbapi()
#     mbapi.run(port=8080)