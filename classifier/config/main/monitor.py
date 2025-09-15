from coffea4bees.classifier.task import Main as _Main


class Main(_Main):
    def run(self, _):
        from coffea4bees.classifier.monitor import Monitor
        from coffea4bees.classifier.monitor.usage import Usage

        Usage.stop()
        try:
            Monitor.current()._listener[1].join()
        except KeyboardInterrupt:
            pass
