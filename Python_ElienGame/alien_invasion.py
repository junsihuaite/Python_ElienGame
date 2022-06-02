import sys
from random import randint
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from star import Star


class AlienInvasion:
    """管理游戏资源和行为的类."""

    def __init__(self):
        """初始化游戏并且创建游戏资源."""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # 创建实例以存储游戏统计信息.
        #   并创建记分牌.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # 创建星星群
        self.stars = pygame.sprite.Group()
        self._create_starry()

        # 创建Play按钮.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """开始游戏的主循环."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        """响应了按键和鼠标事件."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stats.save_high_score()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """当玩家单击Play按钮时开始新游戏."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # 重置游戏设置.
            self.settings.initialize_dynamic_settings()

            # 重置游戏统计信息.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # 清空余下的外星人和子弹.
            self.aliens.empty()
            self.bullets.empty()

            # 创建一群新的外星人并且让飞船居中.
            self._create_fleet()
            self.ship.center_ship()

            # 隐藏鼠标光标.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """响应鼠标按下的事件."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            # 向上移动飞船
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            # 向下移动飞船
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            self.stats.save_high_score()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """响应鼠标松开的事件."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:  # 松开的键是上箭头键
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:  # 松开的键是下箭头键
            self.ship.moving_down = False

    def _fire_bullet(self):
        """创建一颗子弹，并且将其加入编组bullets中."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹的位置并且删除消失的子弹."""
        # 更新子弹的位置.
        self.bullets.update()

        # 删除消失的子弹.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """应对子弹外星人碰撞."""
        # 移除任何碰撞的子弹和外星人.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # 摧毁现有子弹并创建新外星人群.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 提高等级.
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
       检查队列是否处于边缘，
          然后更新舰队中所有外星人的位置。
        """
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星人和飞船碰撞.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 检查是否有外星人到达了屏幕底部.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """检查是否有任何外星人到达屏幕底部."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 对待这个就像船被击中一样.
                self._ship_hit()
                break

    def _ship_hit(self):
        """回应被外星人击中的飞船."""
        if self.stats.ships_left > 0:
            #   将ships_left-1，并且更新记分牌.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空剩余的外星人和子弹.
            self.aliens.empty()
            self.bullets.empty()

            # 创建新外星人群并将飞船放到屏幕底部的中央.
            self._create_fleet()
            self.ship.center_ship()

            # 暂停.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """创建外星人群"""
        # 创建一个外星人并找到一排外星人的数量.
        # 外星人的间距为外星人的宽度.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # 计算屏幕可容纳多少行外星人
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # 创建外星人群.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """创建一个外星人并将其加入当前行."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """如果有任何外星人到达边缘，请做出适当的反应."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整群外星人向下移动，并改变它们的方向."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """更新屏幕上的图像，然后翻到新屏幕."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.stars.draw(self.screen)

        # 绘制分数信息.
        self.sb.show_score()

        # 如果游戏处于非活动状态，则绘制Play按钮.
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def _create_starry(self):
        """ 创建星群 """
        # 创建一个星星并计算一行可容纳多少个星星
        star = Star(self)
        star_width, star_height = star.rect.size
        # 屏幕x方向左右各预留一个星星宽度
        self.availiable_space_x = self.screen.get_rect().width - (2 * star_width)
        # 星星的间距为星星宽度的3倍
        number_stars_x = self.availiable_space_x // (4 * star_width) + 1

        # 计算屏幕可容纳多少行星星
        # 屏幕y方向上下各预留一个星星宽度
        self.availiable_space_y = self.screen.get_rect().height - (2 * star_height)
        # 星星的间距为星星高度的3倍
        number_rows = self.availiable_space_y // (4 * star_height) + 1

        # 创建星群
        for row_number in range(number_rows):
            for star_number in range(number_stars_x):
                self._create_star(star_number, row_number)

    def _create_star(self, star_number, row_number):
        # 创建一个星星并将其加入到当前行
        star = Star(self)
        star.rect.x = randint(0, self.availiable_space_x)
        star.rect.y = randint(0, self.availiable_space_y)
        self.stars.add(star)


if __name__ == '__main__':
    # 创建游戏实例并且运行游戏.
    ai = AlienInvasion()
    ai.run_game()
