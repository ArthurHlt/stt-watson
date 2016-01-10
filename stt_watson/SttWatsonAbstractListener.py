from abc import abstractmethod, ABCMeta


class SttWatsonAbstractListener:
    __metaclass__ = ABCMeta

    @abstractmethod
    def listenHypothesis(self, hypothesis):
        pass

    @abstractmethod
    def listenInterimHypothesis(self, interimHypothesis):
        pass

    @abstractmethod
    def listenPayload(self, payload):
        pass
