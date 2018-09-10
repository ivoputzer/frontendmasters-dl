# frontendmasters-dl
utility docker image based on [OS_FrontendMaster-dl](https://github.com/li-xinyang/OS_FrontendMaster-dl).

### build
```sh
docker build --rm -t frontendmasters-dl .
```

### usage
```sh
# bash, zsh
alias frontendmasters-dl="docker run --rm -v $(pwd):/app/src/Download -i ivoputzer/frontendmasters-dl $@"

# fish
alias frontendmasters-dl "docker run --rm -v (pwd):/app/src/Download -i ivoputzer/frontendmasters-dl $argv"
```
