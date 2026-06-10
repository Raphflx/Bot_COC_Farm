from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.bot.farming import FarmingBot


@pytest.fixture
def controller() -> MagicMock:
    ctrl = MagicMock()
    ctrl.screenshot.return_value = np.zeros((720, 1280, 3), dtype=np.uint8)
    return ctrl


@pytest.fixture
def detector() -> MagicMock:
    return MagicMock()


@pytest.fixture
def farming_bot(controller: MagicMock, detector: MagicMock) -> FarmingBot:
    return FarmingBot(controller, detector)


class TestCollectAll:
    def test_collect_taps_all_found_buildings(
        self, farming_bot: FarmingBot, controller: MagicMock, detector: MagicMock
    ) -> None:
        # Two gold mines, one elixir collector, nothing else
        def find_all_side_effect(screenshot: np.ndarray, template: str) -> list:
            if template == "gold_mine_full":
                return [(100, 200), (300, 200)]
            if template == "elixir_collector_full":
                return [(500, 400)]
            return []

        detector.find_all.side_effect = find_all_side_effect
        count = farming_bot.collect_all()
        assert count == 3
        assert controller.tap.call_count == 3

    def test_collect_skips_missing_templates(
        self, farming_bot: FarmingBot, controller: MagicMock, detector: MagicMock
    ) -> None:
        detector.find_all.side_effect = FileNotFoundError("template not found")
        count = farming_bot.collect_all()
        assert count == 0
        controller.tap.assert_not_called()

    def test_collect_returns_zero_when_nothing_found(
        self, farming_bot: FarmingBot, detector: MagicMock
    ) -> None:
        detector.find_all.return_value = []
        assert farming_bot.collect_all() == 0
