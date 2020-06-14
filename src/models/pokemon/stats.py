class Stats:
    """
    A stats object for a given Pokemon.
    """

    def __init__(self, attack: int, defense: int, special_attack: int, special_defense: int, speed: int, accuracy: int = 100, evasion: int = 100):
        """
        Initializes Stats.
        :param attack: The Pokemon's number of attack points.
        :param defense: The Pokemon's number of defense points.
        :param special_attack: The Pokemon's number of special attack points.
        :param special_defense: The Pokemon's number of special defense points.
        :param speed: The Pokemon's number of speed points.
        :param accuracy: The Pokemon's number of accuracy points. Usually starts at 100.
        :param evasion: The Pokemon's number of evasion points. Usually starts at 100.
        """
        self.attack = attack
        self.defense = defense
        self.special_attack = special_attack
        self.special_defense = special_defense
        self.speed = speed
        self.accuracy = accuracy
        self.evasion = evasion

