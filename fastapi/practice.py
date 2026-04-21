import logging

# logging.basicConfig(
#     level=logging.DEBUG,           # show everything
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',   # nice date format
#     filename='app.log',            # write to file instead of console
#     filemode='w'                   # 'w' = overwrite, 'a' = append (default)
# )

logger = logging.getLogger("practice")
logger.setLevel(logging.DEBUG)  # set logger level to DEBUG

# Handler 1: Console (only show ERROR and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Handler 2: File (show everything)
file_handler = logging.FileHandler('app.log', mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.debug("This only goes to file")
logger.error("This goes to both console and file")


logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")