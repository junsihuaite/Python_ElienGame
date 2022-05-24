class GameStats:
    """外星人入侵的跟踪统计."""
    
    def __init__(self, ai_game):
        """初始化统计信息."""
        self.settings = ai_game.settings
        self.reset_stats()

        # 在活跃状态下开始外星人入侵.
        self.game_active = False

        # 任何情况下都不应该重置最高分.
        self.read_high_score()
        
    def reset_stats(self):
        """初始化在游戏过程中可能更改的统计信息."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def save_high_score(self):
        """将最高分保存在high_score文件中"""
        high_score_str = str(self.high_score)
        filename = 'Highest_score_history.txt'
        with open(filename, 'w') as file_object:
            file_object.write(high_score_str)

    def read_high_score(self):
        """
        读取high_score文件中保存的最高得分
        如果没有记录，则最高分为0
        """
        filename = 'Highest_score_history.txt'
        try:
            with open(filename) as file_object:
                contents = file_object.read()
            self.high_score = int(contents)
        except FileNotFoundError:
            self.high_score = 0