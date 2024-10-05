import logging
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(current_dir, 'log.txt')

logging.basicConfig(
	filename=log_file, 
	level=logging.INFO, 
	format=('%(asctime)s - %(levelname)s - %(message)s')
	)