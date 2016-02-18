import logging

import lymph
from lymph.utils.logging import setup_logger


class StoreInterface(lymph.Interface):

    def apply_config(self, config):
        self.store = config.get_instance('store')
        super(StoreInterface, self).apply_config(config)

    def on_start(self):
        super(StoreInterface, self).on_start()
        logger = setup_logger('sqlalchemy.pool')
        if not self.container.debug:
            logger.setLevel(logging.ERROR)
