class Stats:
    """
    A stats object for a given Pokemon.
    """

    def __init__(self, attack: int, defense: int, special_attack: int, special_defense: int, speed: int, accuracy: int = 100, evasiveness: int = 100):
        """
        Initializes Stats.
        :param attack: The Pokemon's number of attack points.
        :param defense: The Pokemon's number of defense points.
        :param special_attack: The Pokemon's number of special attack points.
        :param special_defense: The Pokemon's number of special defense points.
        :param speed: The Pokemon's number of speed points.
        :param accuracy: The Pokemon's number of accuracy points. Usually starts at 100.
        :param evasiveness: The Pokemon's number of evasiveness points. Usually starts at 100.
        """
        self._attack = attack
        self._defense = defense
        self._special_attack = special_attack
        self._special_defense = special_defense
        self._speed = speed
        self._accuracy = accuracy
        self._evasiveness = evasiveness

    ##
    #   Getter Functions
    ##

    def get_attack(self) -> int:
        return self._attack

    def get_defense(self) -> int:
        return self._defense

    def get_special_attack(self) -> int:
        return self._special_attack

    def get_special_defense(self) -> int:
        return self._special_defense

    def get_speed(self) -> int:
        return self._speed

    def get_accuracy(self) -> int:
        return self._accuracy

    def get_evasiveness(self) -> int:
        return self._evasiveness

