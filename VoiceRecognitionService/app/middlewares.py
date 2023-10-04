from flask import g, request, abort

# test 
def init_middlewares(app):
    @app.before_request
    def _log_request_info():
        app.logger.debug('Headers: %s', request.headers)
        # app.logger.debug('Body: %s', request.get_data())

    @app.errorhandler(500)
    def _internal_server_error(error):
        app.logger.error('Server Error: %s', error)
        return "Internal server error", 500

    @app.errorhandler(Exception)
    def _unhandled_exception(e):
        app.logger.error('Unhandled Exception: %s', e)
        return "Something went wrong", 500
