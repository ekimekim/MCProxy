
LISTEN_ADDR = ('0.0.0.0', 25564)
SERVER_ADDR = ('127.0.0.1', 25565)
LOG_FILE = 'log'
LOG_FORMAT = "%(created)f\t%(asctime)s\t%(levelname)s\t%(message)s"

# Timeout on select(). Should be small.
SELECT_TIMEOUT = 0.1
