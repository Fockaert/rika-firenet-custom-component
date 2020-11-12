import logging
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from homeassistant.components.climate.const import (HVAC_MODE_AUTO,
                                                    HVAC_MODE_HEAT,
                                                    HVAC_MODE_OFF, PRESET_AWAY,
                                                    PRESET_HOME)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)
SCAN_INTERVAL = timedelta(seconds=15)


class RikaFirenetCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, username, password, default_temperature):
        self.hass = hass
        self._username = username
        self._password = password
        self._default_temperature = default_temperature
        self._client = None
        self._stoves = None
        self.platforms = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self.async_update_data,
            update_interval=SCAN_INTERVAL
        )

    async def async_update_data(self):
        try:
            await self.hass.async_add_executor_job(self.update)
        except Exception as exception:
            raise UpdateFailed(exception)

    def setup(self):
        _LOGGER.info("setup()")
        self._client = requests.session()
        self._stoves = self.setup_stoves()

    def get_stoves(self):
        return self._stoves

    def get_default_temperature(self):
        return self._default_temperature

    def connect(self):
        if self.is_authenticated():
            return

        data = {
            'email': self._username,
            'password': self._password
        }

        postResponse = self._client.post('https://www.rika-firenet.com/web/login', data)

        if not ('/logout' in postResponse.text):
            raise Exception('Failed to connect with Rika Firenet')
        else:
            _LOGGER.info('Connected to Rika Firenet')

    def is_authenticated(self):
        if 'connect.sid' not in self._client.cookies:
            return False

        expiresIn = list(self._client.cookies)[0].expires
        epochNow = int(datetime.now().strftime('%s'))

        if expiresIn <= epochNow:
            return False

        return True

    def get_stove_state(self, id):
        self.connect()
        return self._client.get('https://www.rika-firenet.com/api/client/' + id + '/status?nocache=').json()

    def setup_stoves(self):
        self.connect()
        stoves = []
        postResponse = self._client.get('https://www.rika-firenet.com/web/summary')

        soup = BeautifulSoup(postResponse.content, "html.parser")
        stoveList = soup.find("ul", {"id": "stoveList"})

        if stoveList is None:
            return stoves

        for stove in stoveList.findAll('li'):
            stoveLink = stove.find('a', href=True)
            stoveName = stoveLink.attrs['href'].rsplit('/', 1)[-1]
            stove = RikaFirenetStove(self, stoveName, stoveLink.text)
            _LOGGER.info("Found stove : {}".format(stove))
            stoves.append(stove)

        return stoves

    def update(self):
        _LOGGER.info("update()")
        for stove in self._stoves:
            stove.sync_state()

    def set_stove_controls(self, id, data):
        _LOGGER.info("set_stove_control() id: " + id + " data: " + str(data))

        r = self._client.post('https://www.rika-firenet.com/api/client/' + id + '/controls', data)

        for counter in range(0, 10):
            if ('OK' in r.text) == True:
                _LOGGER.info('Stove controls updated')
                return True
            else:
                _LOGGER.info('In progress.. ({}/10)'.format(counter))
                time.sleep(2)

        return False


class RikaFirenetStove:
    def __init__(self, coordinator: RikaFirenetCoordinator, id, name):
        self._coordinator = coordinator
        self._id = id
        self._name = name
        self._previous_temperature = None
        self._state = None

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def __repr__(self):
        return {'id': self._id, 'name': self._name}

    def __str__(self):
        return 'Stove(id=' + self._id + ', name=' + self._name + ')'

    def sync_state(self):
        return self.sync_state_internal(True)

    def sync_state_internal(self, send_message):
        _LOGGER.debug("Updating stove %s", self._id)
        self._state = self._coordinator.get_stove_state(self._id)

    def set_stove_temperature(self, temperature):
        _LOGGER.info("set_stove_temperature(): " + str(temperature))

        data = self.get_control_state()
        data['targetTemperature'] = str(temperature)

        self._coordinator.set_stove_controls(self._id, data)
        self.sync_state()

    def get_control_state(self):
        return self._state['controls']

    def set_presence(self, presence=PRESET_HOME):
        room_thermostat = self.get_room_thermostat()
        _LOGGER.info("set_presence(): " + str(presence) +
                     " current room thermostat: " + str(room_thermostat))

        if presence == PRESET_AWAY:
            self._previous_temperature = room_thermostat
            self.set_stove_temperature(self.get_stove_set_back_temperature())
        elif presence == PRESET_HOME:
            if self._previous_temperature:
                self.set_stove_temperature(self._previous_temperature)
            else:
                self.set_stove_temperature(
                    self._coordinator.get_default_temperature())
            self._previous_temperature = None

    def get_state(self):
        return self._state

    def get_stove_consumption(self):
        return self._state['sensors']['parameterFeedRateTotal']

    def get_stove_runtime(self):
        return self._state['sensors']['parameterRuntimePellets']

    def get_stove_temperature(self):
        return float(self._state['sensors']['inputFlameTemperature'])

    def get_stove_thermostat(self):
        return float(self._state['controls']['targetTemperature'])

    def get_stove_operation_mode(self):
        return float(self._state['controls']['operatingMode'])

    def get_stove_set_back_temperature(self):
        return float(self._state['controls']['setBackTemperature'])

    def is_heating_times_active_for_comfort(self):
        return self._state['controls']['heatingTimesActiveForComfort']

    def is_stove_on(self):
        return float(self._state['controls']['onOff'])

    def get_room_thermostat(self):
        return float(self._state['controls']['targetTemperature'])

    def get_room_temperature(self):
        return float(self._state['sensors']['inputRoomTemperature'])

    def get_room_power_request(self):
        return float(self._state['controls']['RoomPowerRequest'])

    def is_stove_burning(self):
        if self._state['sensors']['statusMainState'] == 4 or self._state['sensors']['statusMainState'] == 5:
            return True
        else:
            return False

    def get_status_text(self):
        return self.get_status()[1]

    def get_status_picture(self):
        return self.get_status()[0]

    def get_hvac_mode(self):
        if not self.is_stove_on():
            return HVAC_MODE_OFF

        if self.get_stove_operation_mode() is 0:
            return HVAC_MODE_HEAT

        if not self.is_heating_times_active_for_comfort():
            return HVAC_MODE_HEAT

        return HVAC_MODE_AUTO

    def set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVAC_MODE_OFF:
            self.turn_off()
        elif hvac_mode == HVAC_MODE_AUTO:
            self.set_heating_times_active_for_comfort(True)
        elif hvac_mode == HVAC_MODE_HEAT:
            self.set_heating_times_active_for_comfort(False)

    def set_heating_times_active_for_comfort(self, active):
        _LOGGER.info("set_heating_times_active_for_comfort(): " + str(active))

        data = self.get_control_state()
        data['onOff'] = True
        data['heatingTimesActiveForComfort'] = active

        self._coordinator.set_stove_controls(self._id, data)
        self.sync_state()

    def turn_off(self):
        _LOGGER.info("turn_off(): ")

        data = self.get_control_state()
        data['onOff'] = False

        self._coordinator.set_stove_controls(self._id, data)
        self.sync_state()

    def get_status(self):
        mainState = self._state['sensors']['statusMainState']
        subState = self._state['sensors']['statusSubState']
        frostStarted = self._state['sensors']['statusFrostStarted']

        if frostStarted:
            return ["/images/status/Visu_Freeze.svg", "Vorstbeveiliging"]

        if mainState == 1:
            if subState == 0:
                return ["/images/status/Visu_Off.svg", "Kachel uit"]
            elif subState == 1:
                return ["/images/status/Visu_Standby.svg", "Standby"]
            elif subState == 2:
                return ["/images/status/Visu_Standby.svg", "Extern contact"]
            elif subState == 3:
                return ["/images/status/Visu_Standby.svg", "Standby"]
            return ["/images/status/Visu_Off.svg", "Substate onbekend"]
        elif mainState == 2:
            return ["/images/status/Visu_Ignition.svg", "Ontsteken"]
        elif mainState == 3:
            return ["/images/status/Visu_Ignition.svg", "Startfase"]
        elif mainState == 4:
            return ["/images/status/Visu_Control.svg", "Pelletmodule"]
        elif mainState == 5:
            if subState == 3 or subState == 4:
                return ["/images/status/Visu_Clean.svg", "Grote Reiniging"]
            else:
                return ["/images/status/Visu_Clean.svg", "Reiniging"]
        elif mainState == 6:
            return ["/images/status/Visu_BurnOff.svg", "Uitdoven"]
        elif mainState == 11 or mainState == 13 or mainState == 14 or mainState == 16 or mainState == 17 or mainState == 50:
            return ["/images/status/Visu_SpliLog.svg", "Hout check"]
        elif mainState == 20 or mainState == 21:
            return ["/images/status/Visu_SpliLog.svg", "Regeling Hout"]

        return ["/images/status/Visu_Off.svg", "Onbekend"]
