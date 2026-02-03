import logging

def setup_logger():
    # Change the millisecond separator from ',' to '.'
    logging.Formatter.default_msec_format = '%s.%03d'
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    return logging.getLogger("ShigureCafeBot")

logger = setup_logger()
