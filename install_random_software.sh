#!/bin/bash

####
# I saw some people say they "Couldn't just install random packages" on their work machine.
#
# This script aims to allow anyone to install any random package they want, as long as 
# they have sudo privileges)!
#
# For perpetual random installations, drop this bad boy into any cron directory you wish, and
# enjoy the freedom of randomly installing software on an hourly, daily, weekly, or even monthly
# basis!
####

# Create an array of packages not already installed
APT_PACKAGES=(`apt list | grep -Ev 'Listing...|installed' | cut -d'/' -f1 | paste -s`)

# Find the max number our psuedo-random number generator can select from
NUM_PACKAGES=${#APT_PACKAGES[@]}

# Get the package index capped at the number of packages available
PKG_IDX=$((${RANDOM} % ${NUM_PACKAGES}))

# Resolve the package
SEL_PKG=${APT_PACKAGES[${PKG_IDX}]}

# Install!
# sudo apt install -y ${SEL_PKG}
echo "${SEL_PKG}"

exit 0