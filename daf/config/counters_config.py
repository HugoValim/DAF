PV_PREFIX = "daf:"
PILATUS_PREFIX = "EMA:B:P300K01:"

counters_config = {
    "eta_counter": {"pv": PV_PREFIX + "m2", "type": "PV", "class": "EpicsSignalRO"},
    "ring_current": {
        "pv": "SI-Glob:AP-CurrInfo:Current-Mon",
        "type": "PV",
        "class": "EpicsSignalRO",
    },
    "pilatus300k": {"pv": PILATUS_PREFIX, "type": "AD", "class": "pilatus300k"},
    "mvs2_diode": {
        "pv": "EMA:A:RIO01:9215B:ai3",
        "type": "PV",
        "class": "EpicsSignalRO",
    },
    "mvs3_diode": {
        "pv": "EMA:B:RIO01:9220A:ai0",
        "type": "PV",
        "class": "EpicsSignalRO",
    },
    "I0": {
        "pv": "EMA:B:RIO01:9220A:ai2",
        "type": "PV",
        "class": "EpicsSignalRO",
    },
    "I1": {
        "pv": "EMA:B:RIO01:9220A:ai2",
        "type": "PV",
        "class": "EpicsSignalRO",
    },
    "I2": {
        "pv": "EMA:B:RIO01:9220A:ai7",
        "type": "PV",
        "class": "EpicsSignalRO",
    },
    "diff_I0": {
        "pv": "EMA:B:RIO02:9220C:ai00",
        "type": "PV",
        "class": "EpicsSignalRO",
    },
    "diff_I1": {
        "pv": "EMA:B:RIO02:9220C:ai01",
        "type": "PV",
        "class": "EpicsSignalRO",
    },
}

# Build Pilatus rois
for i in range(22):
    roi_now = {
        "pv": PILATUS_PREFIX + "ROIStat1:" + str(i + 1) + ":Net_RBV",
        "type": "PV",
        "class": "EpicsSignalRO",
    }
    roi_name = "pilatus300k_roi" + str(i + 1)
    counters_config[roi_name] = roi_now
