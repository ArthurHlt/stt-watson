# stt-watson
Speech to text using watson in python with websocket and record from microphone

## Requirements

- **Python 2.7**
- **Pip**
- **portaudio**, can be installed with `brew install portaudio` (mac) or `apt-get install portaudio19-dev`(linux)

## Installation

Install with pip: `pip install stt-watson`

## Run the playground

Simply run in command line: `stt-watson`

**At the first launch it will create a config file located to `~/.config-stt-watson.yml` and ask you your watson credentials**

## Usage for developers

** You first need a `config.yml` located in the root of your project (this can be override, look at: [Config class](/config/Config.py) )**

Bootstrap example:

```python
from stt_watson.SttWatson import SttWatson
from stt_watson.SttWatsonAbstractListener import SttWatsonAbstractListener

"""
Example of listener to use data given by stt-watson (stt-watson notify hypothesis to his listeners when he receive it)

Hypothesis format:
{
    'confidence': '0.1' // confidence of the sentence or words if exist
    'transcript': 'the transcription of your voice'
}
"""
class MyListener(SttWatsonAbstractListener):
    def __init__(self):
        pass
    """
    This give hypothesis from watson when your sentence is finished
    """
    def listenHypothesis(self, hypothesis):
        print "Hypothesis: {0}".format(hypothesis)

    """
    This give the json received from watson
    """
    def listenPayload(self, payload):
        print(u"Text message received: {0}".format(payload))
    """
    This give hypothesis from watson when your sentence is not finished
    """
    def listenInterimHypothesis(self, interimHypothesis):
        print "Interim hypothesis: {0}".format(interimHypothesis)


myListener = MyListener()
sttWatson = SttWatson('watson_user', 'watson_password')
sttWatson.addListener(myListener)
sttWatson.run()
```



