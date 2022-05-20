# DSPWorks Home Assistant Component
This is a basic Home Assistant Custom Component for DSPWorks Fan, Sensors 💧 and Switches💡.

[![HACS Shield][hacs-shield]](https://github.com/hacs/integration)
[![GitHub][license-shield]](LICENSE.txt)
[![Code style: black][black-shield]](https://github.com/psf/black)

Feel free to ⭐️ this repo to get notified about the latest features!

## Installation

You can either install this integration as an HACS custom component or install it mannually
### Installing with HACS
* Go to the `HACS` tab and select `Integrations`
* Click on `Explore & Download Repositories`
* Search for `DSPWorks` and then download the repo by clicking `Download this repository with HACS`
* *You will then have to restart your Home Assistant instance*
* After that, you can add the Integration as usual by going to `Configuraton > Devices & Services > Add Integration`


### Installing manually

#### Moving custom component to right directory
```
# How your HA config directory should look

config
└── ...
└── configuration.yaml
└── custom_components
    └── dspworks_app
        └── manifest.json
        └── ...
```

You have to move all content in the `custom_components/dspworks_app` directory to the same location in Home Assistant. If a `custom_components` directory does not already exist in your Home Assistant instance, you will have to make one. You can learn more [here](https://developers.home-assistant.io/docs/creating_integration_file_structure#where-home-assistant-looks-for-integrations).

After all of those are in place, you can restart your Home Assistant instance and the component should load.

#### Start the integration
You should be able to now load the integration. This can be done by going to `Configuraton > Devices & Services > Add Integration`

You should be able to search for DSPWorks and then enter your email and password in the popup.
