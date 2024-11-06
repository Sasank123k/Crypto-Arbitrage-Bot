# ml_models/__init__.py

import logging

# Setup logging specific to ml_models
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Initialized the ML Models package.")
