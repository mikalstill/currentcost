#!/usr/bin/python

# Grab data from the current cost envi in the lounge room

import time

import pycurrentcost

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


sensor_map = {
    '0': 'all',
    '1': 'fridge_kitchen',
    '3': 'freezer_laundry',
    '6': 'fridge_laundry',
}


def Collect():
    cc = pycurrentcost.CurrentCostReader(port="/dev/currentcost")

    metrics = {}

    while True:
        reading = cc.get_reading()

        print reading.xml_str
        print 'Temperature: %s' % reading.temperature
        print 'Sensor: %s (%s)' %(reading.sensor_num, sensor_map.get(reading.sensor_num, '???'))
        print 'Watts: %s' % reading.channels[1]['watts']
        print

        registry = CollectorRegistry()
        Gauge('job_last_success_unixtime', 'Last time the current cost daemon saw a reading',
              registry=registry).set_to_current_time()
        Gauge('temp_c', 'Temperature in celcius', registry=registry).set(reading.temperature)
        push_to_gateway('localhost:9091', job="currentcost", registry=registry)

        registry = CollectorRegistry()
        Gauge('job_last_success_unixtime', 'Last time the current cost daemon saw a reading',
              registry=registry).set_to_current_time()
        Gauge('watts', 'Watts consumed instantaneous',
              registry=registry).set(reading.channels[1]['watts'])
        push_to_gateway('localhost:9091',
                        job='currentcost',
                        grouping_key={'instance': sensor_map.get(reading.sensor_num, 'unknown')},
                        registry=registry)


if __name__ == '__main__':
    Collect()
