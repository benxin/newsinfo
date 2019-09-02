from . import index_blue
import logging

@index_blue.route("/")
def index():
    logging.debug("debug")
    logging.info("info")
    logging.warning("warning")
    logging.error("error")
    return "index page"