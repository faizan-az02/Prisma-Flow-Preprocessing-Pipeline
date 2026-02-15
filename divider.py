import logging

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