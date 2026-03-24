import time


class Timer : 
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0.0
        self.running = False

    def start(self):
        """Démarre le timer."""
        if self.running:
            return
        self.start_time = time.perf_counter()  # Plus précis que time.time()
        self.running = True

    def stop(self):
        """Arrête le timer et calcule le temps écoulé."""
        if not self.running:
            return
        end_time = time.perf_counter()
        self.elapsed_time += end_time - self.start_time
        self.running = False

    def reset(self):
        """Réinitialise le timer."""
        self.start_time = None
        self.elapsed_time = 0.0
        self.running = False

    def get_elapsed(self):
        """Retourne le temps écoulé sans arrêter le timer."""
        if self.running:
            return self.elapsed_time + (time.perf_counter() - self.start_time)
        return self.elapsed_time