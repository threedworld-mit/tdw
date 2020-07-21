#
# Usage:
#
# chmod +x run_build.sh
# ./run_build.sh version
#

sudo service lightdm stop
sudo killall Xorg
sudo nvidia-xconfig -a --use-display-device=None --virtual=256x256
sudo /usr/bin/X :0&
DISPLAY=:0.0 ../Build/TDW_v$1.x86_64