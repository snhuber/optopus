# -*- coding: utf-8 -*-
import logging
import os
from pathlib import Path
import pickle
from typing import List
from optopus.settings import (DATA_DIR, STRATEGY_DIR)
from optopus.strategy import Strategy
import jsonpickle

class StrategyRepository:
    """Repository class for mananging strategies
    """
    def __init__(self) -> None:
        self._path = Path(Path.cwd() / DATA_DIR / STRATEGY_DIR)
        self._log = logging.getLogger(__name__)
        jsonpickle.set_preferred_backend('json')
        jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)

    def add(self, item: Strategy) -> None:
        file_name = self._path / (item.strategy_id + '.json')

        serialized = jsonpickle.encode(item)
        try:
            with open(file_name, 'w') as file:
                file.write(serialized)
        except Exception as e:
            self._log.error('Failed to write strategy file', exc_info=True)

    def update(self, item: Strategy) -> None:
        self.add(item)

    def delete(self, item: Strategy) -> None:
        file_name_src = self._path / (item.strategy_id + '.json')
        file_name_dst = self._path / (item.strategy_id + '.json_closed')
        try:
            os.rename(file_name_src, file_name_dst)
        except Exception as e:
            self._log.error('Failed to delete strategy file', exc_info=True)

    def all_items(self) -> List[Strategy]:
        strategies = {}
        for f in self._path.glob('*.json'):
            file_name = self._path / f
            try:
                with open(file_name, 'r') as file:
                    serialized = file.read()
                s = jsonpickle.decode(serialized)
                strategies[s.strategy_id] = s
                self._log.debug(f'Loaded {f}')
            except FileNotFoundError as e:
                self._log.error('Failed to open strategy file', exc_info=True)
        return strategies
