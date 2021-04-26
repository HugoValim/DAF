#!/usr/bin/env sh
# Stop if anything goes wrong.
set -e

# If not root ask for privileges.
if [ "$(id -u)" != 0 ]
then
	sudo -k "$0" "$@"
	exit
fi

### Needs pip3 installed ###
# FIXME: List of requirements is not complete.
pip3 install pandas tqdm xrayutilities

### Needs git installed ###
INSTALL_DIR="/usr/local/scripts/bash/daf"
git clone https://gitlab.cnpem.br/BEAMLINES/EMA/CLI/daf "$INSTALL_DIR"

mkdir -p /etc/profile.d
cat > /etc/profile.d/daf.sh << EOF
export PATH="\$PATH:$INSTALL_DIR/command_line"
EOF
