from flask import g, request, abort
import traceback

# test 
def init_middlewares(app):
    @app.before_request
    def _log_request_info():
        app.logger.debug(f'Headers: {request.headers}')
        # app.logger.debug('Body: %s', request.get_data())

    @app.errorhandler(500)
    def _internal_server_error(error):
        app.logger.error(f'Server Error: {error}')
        return "Internal server error", 500

    @app.errorhandler(Exception)
    def _unhandled_exception(e):
        tb = traceback.format_exc()  # Gets the full traceback
        app.logger.error(f'Unhandled Exception: {e}\n{tb}')
        return "Something went wrong", 500
