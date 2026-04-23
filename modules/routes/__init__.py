from flask import Flask, send_from_directory

def register_all_routes(app: Flask):
    from modules.routes.scrape import scrape_bp
    from modules.routes.process import process_bp
    from modules.routes.outputs import outputs_bp
    from modules.routes.excel import excel_bp
    from modules.routes.prompts import prompts_bp
    from modules.routes.health import health_bp
    from modules.routes.dashboard import dashboard_bp

    app.register_blueprint(scrape_bp)
    app.register_blueprint(process_bp)
    app.register_blueprint(outputs_bp)
    app.register_blueprint(excel_bp)
    app.register_blueprint(prompts_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/")
    def index():
        return send_from_directory(".", "login.html")

    @app.route("/login")
    def login():
        return send_from_directory(".", "login.html")

    @app.route("/dashboard")
    def dashboard():
        return send_from_directory(".", "dashboard.html")

    @app.route("/issuearrange")
    def issue_arrange():
        return send_from_directory(".", "issuearrange.html")
