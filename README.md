# WireGuard

## Config

* Rename and edit file ```.env.example``` to ```.env```
* Rename and edit file ```wireguard.conf.example``` to ```wireguard.conf```
* ```chmod +x wg.sh```

## Commands

* Start WireGuard ```./wg.sh start```
* Stop WireGuard ```./wg.sh stop```
* Restart WireGuard ```./wg.sh restart```
* Show logs WireGuard ```./wg.sh logs```
* Show stats WireGuard ```./wg.sh stat```
* Add new peers ```./wg.sh add <user1> <user2> <user3>```
* Remove peers ```./wg.sh del <user2> <user3>```
* Show peers ```./wg.sh show <user2> <user3>```
* Send peers to telegram ```./wg.sh send <user2> <user3>```

## Install Bot

```bash
apt update && apt install -y python3.9 python3.9-venv
python3.9 -m venv venv
source ./venv/bin/activate
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org python-telegram-bot python-dotenv
deactivate

./start_bot.sh

```
