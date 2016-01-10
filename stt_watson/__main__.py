from stt_watson.SttWatson import SttWatson
from stt_watson.SttWatsonLogListener import SttWatsonLogListener
from config.Config import Config
import os.path
import argparse
import pkgutil
import yaml


def main():
    home = os.path.expanduser("~")
    defaultConfigFile = home + '/.config-stt-watson.yml'
    parser = argparse.ArgumentParser(
        description='Speech to text using watson in python with websocket and record from microphone')

    parser.add_argument('-f', action='store', dest='configFile', default=defaultConfigFile,
                        help='config file',
                        required=False)
    args = parser.parse_args()
    if not os.path.isfile(args.configFile):
        print "Config file '" + args.configFile + "' doesn't exist."
        print "Creating it ..."
        data = pkgutil.get_data('config', 'config.sample.yml')
        Config.Instance().loadConfigFromResource(data)
        watsonConfig = Config.Instance().getWatsonConfig()
        user = raw_input("Watson user: ")
        password = raw_input("Watson password: ")
        watsonConfig["user"] = user
        watsonConfig["password"] = password
        f = open(args.configFile, 'w')
        f.write(yaml.dump(Config.Instance().getConfig()))
        f.close()

    Config.Instance().setConfigFile(args.configFile)
    sttWatsonLogListener = SttWatsonLogListener()
    sttWatson = SttWatson()
    sttWatson.addListener(sttWatsonLogListener)
    sttWatson.run()


if __name__ == "__main__":
    main()
