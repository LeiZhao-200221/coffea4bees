from python.classifier.task import Main as _Main


class Main(_Main):
    def run(self, _):
        from python.classifier.monitor import Monitor
        from python.classifier.monitor.usage import Usage

        Usage.stop()
        try:
            Monitor.current()._listener[1].join()
        except KeyboardInterrupt:
            pass
