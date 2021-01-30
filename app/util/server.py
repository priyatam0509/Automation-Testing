import requests
import logging

class server(object):
    log = logging.getLogger()
    server_ip = "10.80.31.212"
    instance_ip = ""
    networksim_ip = ""

    @classmethod
    def get_site_info(self):
        """
        Returns site info
        """
        # Let's go ahead and grab the ip and set it for return
        self.instance_ip = self.get("tools/ip")
        self.networksim_ip = self.get("network/ip")


        # @TODO adding a route to see if the container is running, not just the simulator
        return {
            "ip": self.instance_ip if self.instance_ip else "1.2.3.4",
            "network": self.networksim_ip if self.networksim_ip else "1.2.3.4",
            "Status": "Online"
        }
    
    @classmethod
    def get(self, action):
        try:
            request = requests.get("http://{}/api/{}".format(self.server_ip, action))
            return request.content.decode('utf-8') if (request.status_code == 200) else ""
        except Exception as e:
            self.log.warning(e)
    
    @classmethod
    def start(self):
        return self.get('start')
    
    @classmethod
    def stop(self):
        return self.get('stop')
    
    @classmethod
    def reset(self, sim_obj):
        try:
            try:
                ip_addr = self.instance_ip.decode('utf-8')
            except:
                ip_addr = self.instance_ip
            request = requests.get(f"http://{ip_addr}/{sim_obj}/reset/")
            return request.content if (request.status_code == 200) else ""
        except Exception as e:
            self.log.warning(e)

if __name__ == '__main__':
    print(
        server.get_site_info()
    )