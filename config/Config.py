import yaml
from utils.Singleton import Singleton
import yaml
import os.path
from utils.Singleton import Singleton


@Singleton
class Config:
    DEFAULT_CONFIG_FILE = "./config.yml"

    def __init__(self):
        self.yamlConfig = {}
        self.configFile = None
        self.setConfigFile(self.DEFAULT_CONFIG_FILE)

    def loadConfigFile(self):
        if not os.path.isfile(self.configFile):
            print "Warning: config file '" + self.configFile + "' not found"
            return
        streamConfig = file(self.configFile, 'r')
        self.yamlConfig = yaml.load(streamConfig)

    def setConfigFile(self, configFile):
        self.configFile = configFile
        self.loadConfigFile()

    def getConfigFile(self):
        return self.configFile

    def getConfigKey(self, key):
        if key not in self.yamlConfig:
            raise Exception("Value for '" + key + "' not found.")
        return self.yamlConfig[key]

    def setConfigKey(self, key, value):
        self.yamlConfig[key] = value

    def getWatsonConfig(self):
        return self.getConfigKey("watson-stt")

    def getAudioChunk(self):
        return self.getConfigKey("audio-chunk")

    def getAudioRate(self):
        return self.getConfigKey("audio-rate")

    def getChannels(self):
        return self.getConfigKey("channels")

    def setWatsonConfig(self, value):
        self.setConfigKey("watson-stt", value)

    def setAudioChunk(self, value):
        self.setConfigKey("audio-chunk", value)

    def setAudioRate(self, value):
        self.setConfigKey("audio-rate", value)

    def setChannels(self, value):
        self.setConfigKey("channels", value)
