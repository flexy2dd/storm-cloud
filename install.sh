#!/bin/bash

: <<'DISCLAIMER'

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

This script is licensed under the terms of the MIT license.
Unless otherwise noted, code reproduced herein
was written for this script.

DISCLAIMER

# script control variables

productname="storm cloud" # the name of the product to install
scriptname="install.sh" # the name of this script

forcesudo="no" # whether the script requires to be ran with root privileges
promptreboot="no" # whether the script should always prompt user to reboot

FORCE=$1
DEVICE_TREE=true
ASK_TO_REBOOT=false
CURRENT_SETTING=false
UPDATE_DB=false

BOOTCMD=/boot/cmdline.txt
CONFIG=/boot/config.txt
APTSRC=/etc/apt/sources.list
INITABCONF=/etc/inittab
BLACKLIST=/etc/modprobe.d/raspi-blacklist.conf
LOADMOD=/etc/modules
DTBODIR=/boot/overlays

# function define

confirm() {
    if [ "$FORCE" == '-y' ]; then
        true
    else
        read -r -p "$1 [y/N] " response < /dev/tty
        if [[ $response =~ ^(yes|y|Y)$ ]]; then
            true
        else
            false
        fi
    fi
}

prompt() {
        read -r -p "$1 [y/N] " response < /dev/tty
        if [[ $response =~ ^(yes|y|Y)$ ]]; then
            true
        else
            false
        fi
}

success() {
    echo -e "$(tput setaf 2)$1$(tput sgr0)"
}

inform() {
    echo -e "$(tput setaf 6)$1$(tput sgr0)"
}

warning() {
    echo -e "$(tput setaf 1)$1$(tput sgr0)"
}

newline() {
    echo ""
}

progress() {
    count=0
    until [ $count -eq $1 ]; do
        echo -n "..." && sleep 1
        ((count++))
    done
    echo
}
sudocheck() {
    if [ $(id -u) -ne 0 ]; then
        echo -e "Install must be run as root. Try 'sudo ./$scriptname'\n"
        exit 1
    fi
}

sysclean() {
    sudo apt-get clean && sudo apt-get autoclean
    sudo apt-get -y autoremove &> /dev/null
}

sysupdate() {
    if ! $UPDATE_DB; then
        echo "Updating apt indexes..." && progress 3 &
        sudo apt-get update 1> /dev/null || { warning "Apt failed to update indexes!" && exit 1; }
        echo "Reading package lists..."
        progress 3 && UPDATE_DB=true
    fi
}

sysupgrade() {
    sudo apt-get upgrade
    sudo apt-get clean && sudo apt-get autoclean
    sudo apt-get -y autoremove &> /dev/null
}

sysreboot() {
    warning "Some changes made to your system require"
    warning "your computer to reboot to take effect."
    newline
    if prompt "Would you like to reboot now?"; then
        sync && sudo reboot
    fi
}

: <<'MAINSTART'

Perform all global variables declarations as well as function definition
above this section for clarity, thanks!

MAINSTART

# checks and init

if [ $forcesudo == "yes" ]; then
    sudocheck
fi

newline
echo "This script will install everything needed to use"
echo "$productname"
newline
warning "--- Warning ---"
newline
echo "Always be careful when running scripts and commands"
echo "copied from the internet. Ensure they are from a"
echo "trusted source."
newline
echo "If you want to see what this script does before"
echo "running it, you should run:"
echo "    \curl -sS github.com/flexy2dd/storm-cloudadafruit/$scriptname"
newline

if confirm "Do you wish to continue?"; then

    newline
    if confirm "You wish update dependencies? [RECOMMENDED]"; then
        newline
        echo "Add some dependencies..."
        apt-get install git build-essential python3-pip python3-pygame python3-dev python3-rpi.gpio python3-pil i2c-tools libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 libasound2-dev

        newline
        echo "Add python dependencies..."
        pip3 install luma.oled configparser python-dateutil simpleaudio python-socketio aiohttp aiodns rpi_ws281x
    fi

    newline
    if confirm "You wish install services? [RECOMMENDED]"; then

        newline
        echo "Installing service..."
        newline
        echo "storm-cloud-manager"
        cp storm-cloud-manager.service /etc/systemd/system/storm-cloud-manager.service
        sudo systemctl daemon-reload
        systemctl disable storm-cloud-manager.service
        
        newline
        echo "storm-cloud-server"
        cp storm-cloud-server.service /etc/systemd/system/storm-cloud-server.service
        sudo systemctl daemon-reload
        systemctl disable storm-cloud-server.service
        
        newline
        echo "storm-cloud-player"
        cp storm-cloud-player.service /etc/systemd/system/storm-cloud-player.service
        sudo systemctl daemon-reload
        systemctl disable storm-cloud-player.service
        
        newline
        echo "You can optionally activate all service in the background at boot."
        newline
        if confirm "Activate service in background? [RECOMMENDED]"; then
	          newline
	          systemctl enable storm-cloud-manager.service
	          systemctl enable storm-cloud-server.service
	          systemctl enable storm-cloud-player.service
	          ASK_TO_REBOOT=False
        fi

    fi

    newline
    success "All done!"
    newline
    echo "Enjoy your new $productname!"
    newline

    if [ $promptreboot == "yes" ] || $ASK_TO_REBOOT; then
        sysreboot
    fi
else
    newline
    echo "Aborting..."
    newline
fi

exit 0
