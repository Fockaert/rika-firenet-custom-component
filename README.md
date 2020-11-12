# Rika Firenet

_Component to integrate with Rika Firenet [rikafirenet]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`climate` | ...
`sensor` | ...

## Planning
* Add readme example graphs possible
* Get the config flow working with update and platform selections
* Support preset mode (in comment atm)
* Support smart target temperature. e.g. Show base temperature when active
* Support Rika stove without external thermostat (only tested with external thermostat)
* ... Open for more stuff ...

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `rika_firenet`.
4. Download _all_ the files from the `custom_components/rika_firenet/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Rika Firenet"

## Configuration is done in the UI

Utility meters example:
```yaml
utility_meter:
  hourly_stove_consumption:
    source: sensor.<stove>_stove_consumption
    cycle: hourly
  daily_stove_consumption:
    source: sensor.<stove>_stove_consumption
    cycle: daily
  weekly_stove_consumption:
    source: sensor.<stove>_stove_consumption
    cycle: weekly
  monthly_stove_consumption:
    source: sensor.<stove>_stove_consumption
    cycle: monthly

  hourly_stove_runtime:
    source: sensor.<stove>_stove_runtime
    cycle: hourly
  daily_stove_runtime:
    source: sensor.<stove>_stove_runtime
    cycle: daily
  weekly_stove_runtime:
    source: sensor.<stove>_stove_runtime
    cycle: weekly
  monthly_stove_runtime:
    source: sensor.<stove>_stove_runtime
    cycle: monthly
```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[rikafirenet]: https://github.com/fockaert/rika-firenet-custom-component
[forum]: https://community.home-assistant.io/
[releases]: https://github.com/fockaert/rika-firenet-custom-component/releases
