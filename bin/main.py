import logging

from client import Client


if __name__ == '__main__':
    logging.basicConfig(
        format="%(levelname)s:%(name)s:%(asctime)s: %(message)s",
        filename='client.log',
        level=logging.DEBUG,
        # datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.debug("##########\n")
    logging.debug("Session started.")
    
    Client.boot_up()
    
    logging.debug("Session ended.")
    logging.debug("\n##########")
