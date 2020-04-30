from openapi_server.__main__ import mbapi

if __name__ == "__main__":
    app = mbapi()
    app.run()
else:
    gunicorn_app = mbapi()