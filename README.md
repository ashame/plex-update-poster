<h1 align="center">Welcome to plex-update-poster 👋</h1>
<p>
  <a href="https://github.com/ashame/plex-update-poster#readme" target="_blank">
    <img alt="Documentation" src="https://img.shields.io/badge/documentation-yes-brightgreen.svg" />
  </a>
  <a href="https://github.com/ashame/plex-update-poster/blob/master/LICENSE" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
</p>

> Command line service that regularly queries a running Plex instance for new titles, and posts them to a REST API

## Configuration

- Make a copy of `data.example.json` named `data.json` and edit values under `credentials`
* ### Credentials - all fields are required
  | key            | value                                                                                                                 |
  |----------------|-----------------------------------------------------------------------------------------------------------------------|
  | imageServerUrl | base url to custom image server (ex. https://img.domain.com) - these are for plex-guid items and are uploaded via ssh |
  | plexServerUrl  | base url to plex server (ex. https://plex.domain.com:12368)                                                           |
  | plexToken      | token for making API requests to plex server - refer section below                                                    |
  | webhookUrl     | url of Discord webhook to post updates                                                                                |
  | sshHostname    | hostname of ssh server                                                                                                |
  | sshUsername    | username to login with                                                                                                |
  | sshKeyFile     | /path/to/key for SSH authentication                                                                                   |

#### Obtaining Plex Token
1. In any modern browser, navigate to the [Plex App](https://app.plex.tv/)
2. Open developer tools or similar, and view the **Network** tab
3. Click on any title in the library of target plex server, and filter for any URLs with `transcode`
4. Look in the URL for `X-Plex-Token`

## Install

```sh
pip install -r requirements.txt
```

## Usage

```sh
python3 __main__.py
```

## Author

👤 **Nathan**

* Github: [@ashame](https://github.com/ashame)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/ashame/plex-update-poster/issues). 

## Show your support

Give a ⭐️ if this project helped you!

## 📝 License

Copyright © 2022 [Nathan](https://github.com/ashame).<br />
This project is [MIT](https://github.com/ashame/plex-update-poster/blob/master/LICENSE) licensed.

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_