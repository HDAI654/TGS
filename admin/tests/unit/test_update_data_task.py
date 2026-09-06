from unittest.mock import MagicMock, patch

import pytest
from celery.exceptions import Ignore

from tgs_admin.apps.worker_control.tasks import UpdateDataLock, update_data


def test_update_data_does_not_release_a_lock_it_does_not_own() -> None:
    lock = MagicMock(spec=UpdateDataLock)
    lock.acquire.return_value = False

    with patch(
        "tgs_admin.apps.worker_control.tasks.UpdateDataLock",
        return_value=lock,
    ):
        with pytest.raises(Ignore):
            update_data.run()

    lock.release.assert_not_called()


def test_update_data_releases_lock_after_success() -> None:
    lock = MagicMock(spec=UpdateDataLock)
    lock.acquire.return_value = True

    with patch(
        "tgs_admin.apps.worker_control.tasks.UpdateDataLock",
        return_value=lock,
    ):
        update_data.run()

    lock.release.assert_called_once_with()


def test_update_data_releases_lock_after_failure() -> None:
    lock = MagicMock(spec=UpdateDataLock)
    lock.acquire.return_value = True

    with patch(
        "tgs_admin.apps.worker_control.tasks.UpdateDataLock",
        return_value=lock,
    ), patch(
        "tgs_admin.apps.worker_control.tasks.logger.info",
        side_effect=[None, RuntimeError("placeholder failure")],
    ):
        with pytest.raises(RuntimeError, match="placeholder failure"):
            update_data.run()

    lock.release.assert_called_once_with()
