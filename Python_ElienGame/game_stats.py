class GameStats:
    """外星人入侵的跟踪统计."""
    
    def __init__(self, ai_game):
        """初始化统计信息."""
        self.settings = ai_game.settings
        self.reset_stats()

        # 在活跃状态下开始外星人入侵.
        self.game_active = True
        
    def reset_stats(self):
        """初始化在游戏过程中可能更改的统计信息."""
        self.ships_left = self.settings.ship_limit