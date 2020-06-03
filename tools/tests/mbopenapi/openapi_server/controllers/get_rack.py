import yaml

def get_rack() -> list:
    """
    Read hostlist file, extract rack list and computer list
    """
    rack_list = []
    comp_list = []
    try:
        with open("./hostlist", 'r') as infile:
        # with open("openapi_server/controllers/hostlist", 'r') as infile:
            data = infile.read()
            list_str = data[1:-1]
            list_arr = list_str.split(', ')
            for item in list_arr:
                hostName = item[1:-1]
                rack_comp = hostName.split(":")[1]
                rack = int(rack_comp.split("-")[1])
                comp = int(rack_comp.split("-")[2])
                if rack not in rack_list:
                    rack_list.append(rack)
                if comp not in comp_list:
                    comp_list.append(comp)
    except Exception as err:
        print(err)
    print("Rack list: ", rack_list)
    print("Computer list: ", comp_list)


get_rack()