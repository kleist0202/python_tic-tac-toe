class Player:
    def __init__(self, points, user_tag):
        self.points = points
        self.user_tag = user_tag
        self.turn = "player_1"
        self.changed = False
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.new_game = False
        self.starting_turn = self.turn

    def serialize(self):
        return {
            "points": self.points,
            "user_tag": self.user_tag,
            "turn": self.turn,
            "changed": self.changed,
            "board": self.board,
            "new_game": self.new_game,
            "starting_turn": self.starting_turn,
        }

    def __repr__(self) -> str:
        return (
            f"Player({self.points=}, {self.user_tag=}, {self.turn=}, {self.changed=})"
        )

    @classmethod
    def deserialize(cls, data):
        points = data["points"]
        user_tag = data["user_tag"]
        turn = data["turn"]
        changed = data["changed"]
        board = data["board"]
        new_game = data["new_game"]
        starting_turn = data["starting_turn"]

        player = cls(points, user_tag)
        player.turn = turn
        player.changed = changed
        player.board = board
        player.new_game = new_game
        player.starting_turn = starting_turn
        return player
