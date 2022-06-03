import unittest
from alien import Alien
from alien_invasion import AlienInvasion
from pymouse import PyMouse
from unittest.mock import Mock


class Test_Alien(unittest.TestCase):
    """测试外星人"""

    def test_click_play_button(self):
        """测试点击按钮"""
        ai = AlienInvasion()
        mock_g = Mock(return_value=ai)
        mock_obj = mock_g()

        # 测试游戏是否为非活动状态
        self.assertEqual(mock_obj.stats.game_active, False)
        # 点击按钮
        m = PyMouse()
        m.click(736, 439)
        # 更新游戏状态
        mock_obj._check_events()
        # 游戏是否为活动状态
        self.assertEqual(mock_obj.stats.game_active, True)

    def test_left_edges(self):
        # 当外星人到屏幕左边时返回True
        alien_main = AlienInvasion()
        alien = Alien(alien_main)
        alien.rect.left = 0
        self.assertEqual(alien.check_edges(), True)

    def test_right_edges(self):
        # 当外星人到屏幕右边时返回True
        alien_main = AlienInvasion()
        alien = Alien(alien_main)
        alien.rect.right = alien_main.screen.get_rect().right
        self.assertEqual(alien.check_edges(), True)
