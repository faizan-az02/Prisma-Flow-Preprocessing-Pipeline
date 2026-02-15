import logging

logging.basicConfig(
    filename="log.txt",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True,
)

def divider():
    
    logger = logging.getLogger()
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler):
            h.flush()
            h.stream.write("-" * 32 + "\n")
            h.flush()
            break
    else:
        logging.info("-" * 32)