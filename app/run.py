from sys import argv

if __name__ == '__main__':
    from configs import flask_configs
    from main import app as working_app

    port = argv[1]
    host = argv[2]

    working_app.config.from_mapping(flask_configs)
    working_app.run(host=host, port=port)
