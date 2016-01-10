from stt_watson.SttWatsonAbstractListener import SttWatsonAbstractListener


class SttWatsonLogListener(SttWatsonAbstractListener):
    def __init__(self):
        pass

    def listenHypothesis(self, hypothesis):
        print "Hypothesis: {0}".format(hypothesis)

    def listenPayload(self, payload):
        print(u"Text message received: {0}".format(payload))

    def listenInterimHypothesis(self, interimHypothesis):
        print "Interim hypothesis: {0}".format(interimHypothesis)
