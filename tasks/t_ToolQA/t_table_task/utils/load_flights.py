from .utils import db_loader, CORPUS_DIR

DATA_FLIGHTS = db_loader(CORPUS_DIR['flights'], 'flights')
