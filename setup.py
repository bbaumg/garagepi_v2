import setuptools 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
	name='garagepi',
	version='2.0.0',
	description='Garage Sensor',
	url='https://github.com/bbaumg/garagepi_v2',
	author='bbaumg',
	license='MIT',
	install_requires=['smbus', 'paho-mqtt',
    'RPi.GPIO', 'pyyaml', 'bme280==1.0.3', 'thingspeak>=1.1.1'],
  dependency_links=['https://github.com/bbaumg/Python_BME280/tarball/master#egg=bme280-1.0.3',
    'https://github.com/bbaumg/Python_Thingspeak/tarball/master#egg=thingspeak-1.1.1'
  ]
)

input("\n\nInstall is complete\nRename and update setting.yaml:  ")