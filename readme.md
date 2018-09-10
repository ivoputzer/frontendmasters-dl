# frontendmasters-dl
utility docker image based on [OS_FrontendMaster-dl](https://github.com/li-xinyang/OS_FrontendMaster-dl).

### build
```sh
docker build --rm -t ivoputzer/frontendmasters-dl .
```

### usage
```sh
# bash, zsh
alias frontendmasters-dl="docker run --rm -v $(pwd):/app/src/Download -i ivoputzer/frontendmasters-dl $@"

# fish
alias frontendmasters-dl "docker run --rm -v (pwd):/app/src/Download -i ivoputzer/frontendmasters-dl $argv"

frontendmasters-dl --help
```

### options
```
Usage: frontendmasters-dl [OPTIONS]

Options:
  --course TEXT      Course ID (e.g. `firebase-react`)
  --id TEXT          Frontend Master Username
  --password TEXT    Frontend Master Password
  --mute-audio       Mute Frontend Master browser tab
  --high-resolution  Download high resolution videos
  --video-per-video  Download one video at a time
  --help             Show this message and exit.
```
