import yaml
from utils.Singleton import Singleton


@Singleton
class Config:
    CONFIG_FILE = "./config.yml"

    def __init__(self):
        streamConfig = file(self.CONFIG_FILE, 'r')
        self.yamlConfig = yaml.load(streamConfig)

    def getWatsonConfig(self):
        return self.yamlConfig["watson-stt"]

    def getAudioChunk(self):
        return self.yamlConfig["audio-chunk"]

    def getAudioRate(self):
        return self.yamlConfig["audio-rate"]

    def getChannels(self):
        return self.yamlConfig["channels"]
