import subprocess

docker_networks_str = subprocess.check_output(['docker', 'network', 'ls'])
docker_networks_ids = [s[:12] for s in docker_networks_str.split("\n")[1:-1]]

def get_network_subnet(network_id):
    network_inspect = subprocess.check_output(['docker', "network", 'inspect', network_id])
    if "Subnet" in network_inspect:
        return network_inspect.split("Subnet\": \"")[1].split("\"")[0]
    
networks_subnets = filter(lambda x : x, [get_network_subnet(network_id) for network_id in docker_networks_ids])

for i in range(50, 250):
    subnet = "172.16."+str(i)+".0/24"
    if subnet not in networks_subnets:
        print subnet
        break