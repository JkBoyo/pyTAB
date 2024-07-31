class os_info:
    def __init__(self):
        self.pretty_name
        self.name
        self.version_id
        self.version
        self.version_codename
        self.id
        self.home_url
        self.support_url
        self.bug_report_url
        self.codename


class hw_info:
    def __init__(self, hw_dict: dict):
        self.id = hw_dict["id"]
        self.Class = hw_dict["class"]
        self.claimed = hw_dict["claimed"]
        self.physid = hw_dict["physid"]


class cpu_info(hw_info):
    def __init__(self, cpu_dict: dict):
        super().__init__(cpu_dict)
        self.product = cpu_dict["product"]
        if "intel" in cpu_dict["vendor"].lower():
            self.vendor = "Intel"
        elif "amd" in cpu_dict["vendor"].lower():
            self.venodor = "Amd"
        self.businfo = cpu_dict["businfo"]
        self.units = cpu_dict["units"]
        self.size = cpu_dict["size"]
        self.capacity = cpu_dict["capacity"]
        self.width = cpu_dict["width"]
        self.capabilities = cpu_dict["capabilities"]


class gpu_info(hw_info):
    def __init__(self, gpu_dict):
        super().__init__(gpu_dict)
        self.handle = gpu_dict["handle"]
        self.description = gpu_dict["description"]
        self.product = gpu_dict["product"]
        if "intel" in gpu_dict["vendor"].lower():
            self.vendor = "Intel"
        elif "amd" in gpu_dict["vendor"].lower():
            self.venodor = "Amd"
        elif "nvidia" in gpu_dict["vendor"].lower():
            self.vendor = "Nvidia"
        self.businfo = gpu_dict["businfo"]
        self.version = gpu_dict["version"]
        self.width = gpu_dict["width"]
        self.clock = gpu_dict["clock"]
        self.configuration = configuration(gpu_dict["configuration"])
        self.capabilities = gpu_dict["capabilities"]


class memory(hw_info):
    def __init__(self, memory_dict):
        super().__init__(memory_dict)
        self.description = memory_dict["description"]
        self.units = memory_dict["units"]
        if memory_dict["size"] == "gigabytes":
            self.units = "gb"
        elif memory_dict["size"] == "megabytes":
            self.units = "mb"
        elif memory_dict["size"] == "bytes":
            self.units = "b"


class configuration:
    def __init__(self, config_dict):
        self.driver = config_dict["driver"]
        self.latency = config_dict["latency"]
