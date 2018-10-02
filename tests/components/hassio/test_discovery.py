"""Test config flow."""
from unittest.mock import patch, Mock

from homeassistant.const import EVENT_HOMEASSISTANT_START

from tests.common import mock_coro


async def test_hassio_discovery_startup(hass, aioclient_mock, hassio_client):
    """Test startup and discovery after event."""
    aioclient_mock.get(
        "http://127.0.0.1/discovery", json={
            'result': 'ok', 'data': {'discovery': [
                {
                    "service": "mqtt", "uuid": "test",
                    "addon": "mosquitto", "config":
                    {
                        'broker': 'mock-broker',
                        'port': 1883,
                        'username': 'mock-user',
                        'password': 'mock-pass',
                        'protocol': '3.1.1'
                    }
                }
            ]}})
    aioclient_mock.get(
        "http://127.0.0.1/addons/mosquitto/info", json={
            'result': 'ok', 'data': {'name': "Mosquitto Test"}
        })

    with patch('homeassistant.components.mqtt.'
               'config_flow.FlowHandler.async_step_hassio',
               Mock(return_value=mock_coro())) as mock_mqtt:
        hass.bus.async_fire(EVENT_HOMEASSISTANT_START)
        await hass.async_block_till_done()

        assert aioclient_mock.call_count == 2
        assert mock_mqtt.called
        mock_mqtt.assert_called_with({
            'broker': 'mock-broker', 'port': 1883, 'username': 'mock-user',
            'password': 'mock-pass', 'protocol': '3.1.1'
        })