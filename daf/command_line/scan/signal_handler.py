import time

from bluesky.utils import SigintHandler


class DAFSigIntHandler(SigintHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals_map = {
            "r": self._RE.resume,
            "resume": self._RE.resume,
            "a": self._RE.abort,
            "abort": self._RE.abort,
            "h": self._RE.halt,
            "halt": self._RE.halt,
            "s": self._RE.stop,
            "stop": self._RE.stop,
        }

    def handle_sigint(self, defer: bool):

        self._RE.request_pause(defer)
        while True:
            user_response = input(
                "RunEngine is paused, what do you want to do? , Resume(r), Abort(a), Stop(stop), Halt(h) \n\n"
            )
            if user_response.lower() not in self.signals_map.keys():
                continue
            self.signals_map[user_response]()
            break

    def handle_signals(self):
        # Check for pause requests from keyboard.
        # TODO, there is a possible race condition between the two
        # pauses here
        if self._RE.state.is_running and (not self._RE._interrupted):
            if (
                self.last_sigint_time is None
                or time.time() - self.last_sigint_time > 10
            ):
                # reset the counter to 1
                # It's been 10 seconds since the last SIGINT. Reset.
                self.count = 1
                if self.last_sigint_time is not None:
                    self.log.debug(
                        "It has been 10 seconds since the "
                        "last SIGINT. Resetting SIGINT "
                        "handler."
                    )
                print(
                    "A 'deferred pause' has been requested. The "
                    "RunEngine will pause at the next checkpoint. "
                    "To pause immediately, hit Ctrl+C again in the "
                    "next 10 seconds."
                )
                self.handle_sigint(True)
            elif self.count == 2:
                print("trying a second time")
                # - Ctrl-C twice within 10 seconds -> hard pause
                self.log.debug(
                    "RunEngine detected two SIGINTs. " "A hard pause will be requested."
                )
                self.handle_sigint(False)
            self.last_sigint_time = time.time()
