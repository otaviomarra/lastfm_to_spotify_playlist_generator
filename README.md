# Spotify playlist generator from Lastfm

Generate spotify playlists based on your lastfm records! Download your lastfm played tracks, clusterize and generate new playlists on Spotify on demand

## Installing / Getting started

Make sure all libraries from [requirements.txt](https:\\link) are installed

The project was written using Selenium with Firefox to open a browser window for the user to authentication. Make sure you have both Firefox and the [Geckodriver](https://github.com/mozilla/geckodriver) plugin installed (you can also change to another browser on the [utils/spotify_api.py](https://link) file at line 288)

### Initial Configuration

You will need to have acces to both lastfm and spotify apis (check links below to get you api tokens)

**Lastfm API** : [Last.fm API account](https://www.last.fm/api)<br>
**Spotify** : [Spotify for developers](https://developer.spotify.com/) - log in with you Spotify account and create a new app

After that, create a `.env` file on root, following the example below:

```
LASTFM_USER = "username"
LASTFM_API_KEY = "apikey"
SPOTIFY_CLIENT_ID = "clientid"
SPOTIFY_CLIENT_SECRET = "clientsecret"
```
No need to worry with the Spotify's user authentication - it will be made via browser when needed

## Developing

Here's a brief intro about what a developer must do in order to start developing
the project further:

```shell
git clone https://github.com/your/awesome-project.git
cd awesome-project/
packagemanager install
```

And state what happens step-by-step.

### Docker version (wip)
**IMPORTANT:** Further development to allow te browser GUI to be opened (probably with a vnc) is still missing. Therefore, the current Dockerfile is still not working

## Features

What's all the bells and whistles this project can perform?
* What's the main functionality
* You can also do another thing
* If you get really randy, you can even do this

## Configuration

Here you should write what are all of the configurations a user can enter when
using the project.

#### Argument 1
Type: `String`  
Default: `'default value'`

State what an argument does and how you can use it. If needed, you can provide
an example below.

Example:
```bash
awesome-project "Some other value"  # Prints "You're nailing this readme!"
```

#### Argument 2
Type: `Number|Boolean`  
Default: 100

Copy-paste as many of these as you need.

## Contributing

When you publish something open source, one of the greatest motivations is that
anyone can just jump in and start contributing to your project.

These paragraphs are meant to welcome those kind souls to feel that they are
needed. You should state something like:

"If you'd like to contribute, please fork the repository and use a feature
branch. Pull requests are warmly welcome."

If there's anything else the developer needs to know (e.g. the code style
guide), you should link it here. If there's a lot of things to take into
consideration, it is common to separate this section to its own file called
`CONTRIBUTING.md` (or similar). If so, you should say that it exists here.

## Links

Even though this information can be found inside the project on machine-readable
format like in a .json file, it's good to include a summary of most useful
links to humans using your project. You can include links like:

- Project homepage: https://your.github.com/awesome-project/
- Repository: https://github.com/your/awesome-project/
- Issue tracker: https://github.com/your/awesome-project/issues
  - In case of sensitive bugs like security vulnerabilities, please contact
    my@email.com directly instead of using issue tracker. We value your effort
    to improve the security and privacy of this project!
- Related projects:
  - Your other project: https://github.com/your/other-project/
  - Someone else's project: https://github.com/someones/awesome-project/


## Licensing

One really important part: Give your project a proper license. Here you should
state what the license is and how to find the text version of the license.
Something like:

"The code in this project is licensed under MIT license."
