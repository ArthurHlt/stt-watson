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
            return
        streamConfig = file(self.configFile, 'r')
        self.loadConfigFromResource(streamConfig)

    def loadConfigFromResource(self, resource):
        self.yamlConfig = yaml.load(resource)

    def setConfigFile(self, configFile):
        self.configFile = configFile
        self.loadConfigFile()

    def getConfigFile(self):
        return self.configFile

    def getConfigKey(self, key):
        if key not in self.yamlConfig:
            if not os.path.isfile(self.configFile):
                raise Exception("Config file '" + self.configFile + "' not found.")
            raise Exception("Value for '" + key + "' not found.")
        return self.yamlConfig[key]

    def getConfig(self):
        return self.yamlConfig

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
