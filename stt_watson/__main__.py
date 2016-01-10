from stt_watson.SttWatson import SttWatson
from stt_watson.SttWatsonLogListener import SttWatsonLogListener
from config.Config import Config
import argparse


def main():
    sttWatsonLogListener = SttWatsonLogListener()
    sttWatson = SttWatson()
    sttWatson.addListener(sttWatsonLogListener)
    sttWatson.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Speech to text using watson in python with websocket and record from microphone')

    parser.add_argument('-f', action='store', dest='configFile', default='./config.yml', help='config file',
                        required=True)
    args = parser.parse_args()
    Config.Instance().setConfigFile(args.configFile)
    main()
