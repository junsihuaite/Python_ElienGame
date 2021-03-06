import unittest
from unittest.mock import Mock
import win32api
import win32con
from unittest import TestCase
from alien_invasion import AlienInvasion


class TestShipMove(TestCase):

    def test_ship_moving_left(self):
        """飞船左移的测试"""
        ai = AlienInvasion()
        mock_g = Mock(return_value=ai)
        mock_obj = mock_g()

        # 按下左键
        win32api.keybd_event(37, 0, 0, 0)
        # 更新游戏状态
        for i in range(100):
            mock_obj._check_events()
            mock_obj.ship.update()
        # 按下左键时标志是否为True
        self.assertEqual(mock_obj.ship.moving_left, True)
        # 判断飞船是否出界
        self.assertEqual(mock_obj.ship.rect.left >= 0, True)

        # 松开左键
        win32api.keybd_event(37, 0, win32con.KEYEVENTF_KEYUP, 0)
        mock_obj._check_events()
        mock_obj.ship.update()
        # 判断松开左键后标志是否变为False
        self.assertEqual(mock_obj.ship.moving_left, False)

    def test_ship_moving_right(self):
        """飞船右移的测试"""
        ai = AlienInvasion()
        mock_g = Mock(return_value=ai)
        mock_obj = mock_g()

        # 按下右键
        win32api.keybd_event(39, 0, 0, 0)
        # 更新游戏状态
        for i in range(100):
            mock_obj._check_events()
            mock_obj.ship.update()
        # 按下右键时标志是否为True
        self.assertEqual(mock_obj.ship.moving_right, True)
        self.assertEqual(mock_obj.ship.rect.right <= mock_obj.screen.get_rect().right, True)

        # 松开右键
        win32api.keybd_event(39, 0, win32con.KEYEVENTF_KEYUP, 0)
        mock_obj._check_events()
        mock_obj.ship.update()
        # 判断松开右键后标志是否变为False
        self.assertEqual(mock_obj.ship.moving_right, False)


if __name__ == '__main__':
    unittest.main()
