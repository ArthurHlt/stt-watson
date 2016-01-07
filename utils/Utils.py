import requests  # python HTTP requests library


class Utils:
    @staticmethod
    def getAuthenticationToken(hostname, serviceName, username, password):
        uri = hostname + "/authorization/api/v1/token?url=" + hostname + '/' + serviceName + "/api"
        uri = uri.replace("wss://", "https://");
        uri = uri.replace("ws://", "https://");
        print uri
        resp = requests.get(uri, auth=(username, password), verify=False, headers={'Accept': 'application/json'},
                            timeout=(30, 30))
        print resp.text
        jsonObject = resp.json()
        return jsonObject['token']
