import os
import math
import platform
import clr
import sys
import time
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List

dll_path = os.path.join(os.path.dirname(__file__), "../../external/LibreHardwareMonitor/LibreHardwareMonitorLib.dll")
clr.AddReference(dll_path)
from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType

computer = Computer()
computer.IsGpuEnabled = True
computer.IsCpuEnabled = True
computer.Open()

def update_hardware(hardware):
    hardware.Update()
    for subhardware in hardware.SubHardware:
        subhardware.Update()

# Funciones para obtener valores (adaptadas de las que ya tenías)
def get_gpu_vram():
    for hardware in computer.Hardware:
        if hardware.HardwareType.ToString() in ["GpuNvidia", "GpuAmd", "GpuIntel"]:
            hardware.Update()
            for sensor in hardware.Sensors:
                if sensor.SensorType == SensorType.Temperature and sensor.Name == "GPU Memory":
                    return sensor.Value
    return None

def get_gpu_hotspot():
    for hardware in computer.Hardware:
        if hardware.HardwareType.ToString() in ["GpuNvidia", "GpuAmd", "GpuIntel"]:
            hardware.Update()
            for sensor in hardware.Sensors:
                if sensor.SensorType == SensorType.Temperature and sensor.Name == "GPU Hot Spot":
                    return sensor.Value
    return None

def get_gpu_power_watts():
    for hardware in computer.Hardware:
        if hardware.HardwareType.ToString() in ["GpuNvidia", "GpuAmd", "GpuIntel"]:
            hardware.Update()
            for sensor in hardware.Sensors:
                if sensor.SensorType == SensorType.Power and sensor.Name == "GPU Package":
                    return sensor.Value
    return None

def get_cpu_power_watts():
    for hardware in computer.Hardware:
        if hardware.HardwareType == HardwareType.Cpu:
            hardware.Update()
            for sensor in hardware.Sensors:
                # Aquí el sensor puede llamarse "Package" o parecido
                if sensor.SensorType == SensorType.Power and "package" in sensor.Name.lower():
                    return sensor.Value
    return None

class CustomDataSource(ABC):
    @abstractmethod
    def as_numeric(self) -> float:
        pass

    @abstractmethod
    def as_string(self) -> str:
        pass

    @abstractmethod
    def last_values(self) -> List[float]:
        pass

class CPUWatts(CustomDataSource):
    _history: List[float] = []

    def as_numeric(self) -> float:
        value = get_cpu_power_watts()
        if value is not None and math.isfinite(value):
            self._history.append(value)
            return value
        return 0.0

    def as_string(self) -> str:
        val = self.as_numeric()
        # truncamos la parte decimal
        return f"{int(val)} W" if val > 0 else "0 W"

    def last_values(self) -> List[float]:
        return self._history[-10:]

class GPUWatts(CustomDataSource):
    _history: List[float] = []

    def as_numeric(self) -> float:
        value = get_gpu_power_watts()
        if value is not None and math.isfinite(value):
            self._history.append(value)
            return value
        return 0.0

    def as_string(self) -> str:
        val = self.as_numeric()
        return f"{int(val)} W" if val > 0 else "0 W"

    def last_values(self) -> List[float]:
        return self._history[-10:]

class GPUHotspotTemp(CustomDataSource):
    _history: List[float] = []

    def as_numeric(self) -> float:
        value = get_gpu_hotspot()
        if value is not None and math.isfinite(value):
            self._history.append(value)
            return value
        return 0.0

    def as_string(self) -> str:
        val = self.as_numeric()
        return f"{int(val)}ºC" if val > 0 else "0ºC"

    def last_values(self) -> List[float]:
        return self._history[-10:]

class GPUVRAMTemp(CustomDataSource):
    _history: List[float] = []

    def as_numeric(self) -> float:
        value = get_gpu_vram()
        if value is not None and math.isfinite(value):
            self._history.append(value)
            return value
        return 0.0

    def as_string(self) -> str:
        val = self.as_numeric()
        return f"{int(val)}ºC" if val > 0 else "0ºC"

    def last_values(self) -> List[float]:
        return self._history[-10:]
