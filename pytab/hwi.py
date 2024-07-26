#!/usr/bin/env python3

# pytab.hwi.py
# A transcoding hardware benchmarking client (for Jellyfin)
#    Copyright (C) 2024 BotBlake <B0TBlake@protonmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##########################################################################################
import platform
from json import dumps

import click
import cpuinfo

if platform.system() == "Windows":
    import wmi


def get_platform_id(platforms: list) -> str:
    for element in platforms:
        if platform.system().lower() == element["type"].lower():
            return element["id"]


def get_os_info() -> dict:
    required = [
        "pretty_name",
        "name",
        "version_id",
        "version",
        "version_codename",
        "id",
        "home_url",
        "support_url",
        "bug_report_url",
    ]
    os_element = dict()

    # Getting system name, release and version
    os_element["name"] = platform.system()
    os_element["version"] = platform.version()
    os_element["version_id"] = platform.release()

    # Filling all possible values
    if os_element["name"] == "Linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    key, value = line.strip().split("=", 1)
                    value = value.strip('"')
                    if key.lower() in required:
                        os_element[key.lower()] = value
        except FileNotFoundError:
            os_element["pretty_name"] = "Linux (Unknown Distro)"
            os_element["id"] = "linux"

    elif os_element["name"] == "Windows":
        os_element["pretty_name"] = platform.system() + " " + platform.release()
        os_element["id"] = "windows"
        os_element["version_codename"] = "win32"
        os_element["home_url"] = "https://www.microsoft.com/windows"
        os_element["support_url"] = "https://support.microsoft.com"
        os_element["bug_report_url"] = "https://support.microsoft.com/contactus/"

    return os_element


def get_gpu_info() -> list:
    gpu_elements = list()
    if platform.system() == "Windows":
        c = wmi.WMI()
        gpus = c.Win32_VideoController()

        for i, gpu in enumerate(gpus):
            configuration = {
                "driver": gpu.DriverVersion.strip(),
            }

            vendor = gpu.AdapterCompatibility.strip().lower()
            gpu_element = {
                "id": f"GPU{i+1}",
                "class": "display",
                "description": gpu.creationClassName.strip(),
                "product": gpu.Name,
                "vendor": vendor,
                "physid": gpu.DeviceID.strip(),
                "businfo": gpu.PNPDeviceID.strip(),
                "configuration": configuration,
            }
            gpu_elements.append(gpu_element)

    elif platform.system() == "Linux":
        click.echo(" Error")
        click.echo()
        click.echo("ERROR: Linux Hardware information not yet supported", err=True)
        click.pause("Press any key to exit")
        exit()
    else:
        click.echo("Error")
        click.echo()
        click.echo(
            "ERROR: Unsupported OS, Hardware information not supported", err=True
        )
        click.pause("Press any key to exit")
        exit()
    return gpu_elements


def get_cpu_info() -> list:
    cpu_info = cpuinfo.get_cpu_info()
    cpu_elements = list()
    vendor = cpu_info["vendor_id_raw"]
    if "intel" in vendor.lower():
        vendor = "Intel"
    elif "amd" in vendor.lower() or "advanced micro devices" in vendor.lower():
        vendor = "Amd"

    cpu_element = {
        "product": cpu_info["brand_raw"],
        "vendor": vendor,
        "cores": cpu_info["count"],
        "architecture": cpu_info["arch_string_raw"],
        "hz_advertised": cpu_info["hz_advertised"][0],
        # "capabilities": cpu_info["flags"],  <- Temporarily Ignoring CPU Features
    }
    cpu_elements.append(cpu_element)

    return cpu_elements


def get_ram_info() -> list:
    ram_modules = list()
    if platform.system() == "Windows":
        c = wmi.WMI()
        for ram in c.Win32_PhysicalMemory():
            capacity = int(ram.Capacity) // (1024**3)  # Convert bytes to gigabytes
            speed = ram.Speed
            form_factor = ram.FormFactor
            ram_module = {
                "id": ram.Tag.strip().replace(" ", "_"),
                "class": "memory",
                "physid": ram.PartNumber,
                "units": "gigabytes",
                "size": capacity,
                "vendor": ram.Manufacturer,
                "Speed": speed,
                "FormFactor": form_factor,
            }
            ram_modules.append(ram_module)
    return ram_modules


def get_system_info() -> dict:
    system_info = {
        "os": get_os_info(),
        "cpu": get_cpu_info(),
        "memory": get_ram_info(),
        "gpu": get_gpu_info(),
    }
    return system_info


if __name__ == "__main__":
    system_info = get_system_info()
    print(dumps(system_info, indent=4))
