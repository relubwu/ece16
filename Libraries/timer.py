from timeit import default_timer


class Timer:
    def __init__(self, period, start_time=0):
        self.start_time = start_time
        self.period = period

    def time_up(self):
        now = default_timer()
        if now - self.start_time > self.period:
            return True
        else:
            return False

    def reset(self):
        self.start_time = default_timer()
