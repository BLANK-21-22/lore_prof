if __name__ == '__main__':
    from configs import flask_configs
    from main import app as working_app

    working_app.config.from_mapping(flask_configs)
    working_app.run()
