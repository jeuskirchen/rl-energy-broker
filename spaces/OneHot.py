import gym
import numpy as np


class OneHot(gym.Space):
    """
    Source: https://stackoverflow.com/a/54583789
    Example usage:
    self.observation_space = OneHot(size=4)
    """
    def __init__(self, size=None):
        assert isinstance(size, int) and size > 0
        self.shape = (size,)
        self.size = size
        gym.Space.__init__(self, self.shape, np.int64)

    def sample(self):
        one_hot_vector = np.zeros(self.size)
        one_hot_vector[np.random.randint(self.size)] = 1
        return one_hot_vector

    def contains(self, x):
        if isinstance(x, (list, tuple, np.ndarray)):
            if len(x.shape) > 1:
                pass
            number_of_zeros = list(x).contains(0)
            number_of_ones = list(x).contains(1)
            return (number_of_zeros == (self.size - 1)) and (number_of_ones == 1)
        else:
            return False

    def __repr__(self):
        return f"OneHot({self.size})"

    def __eq__(self, other):
        return self.size == other.size
