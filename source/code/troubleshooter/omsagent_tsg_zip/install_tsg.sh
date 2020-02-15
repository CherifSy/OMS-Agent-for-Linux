#!/bin/bash
bin_path="/opt/microsoft/omsagent/bin/"
omsagent_tsg_path = "${bin_path}/omsagent_tsg"
plugin_tsg_path="/opt/microsoft/omsagent/plugin/troubleshooter"

echo "Getting ready to install troubleshooter..."

# set up machine

if [ -d $plugin_tsg_path ]; then
    # get rid of old files to update
    echo "Removing older version of troubleshooter..."
    rm -rf $plugin_tsg_path
    rm -f $omsagent_tsg_path
fi

# copy over files
echo "Installing troubleshooter on machine..."
mkdir $plugin_tsg_path
cp -r tsg_code $plugin_tsg_path
cp -r tsg_files $plugin_tsg_path
cp omsagent_tsg $bin_path

echo "You can now run the troubleshooter by going to /opt/microsoft/omsagent/bin/ and running the below command:"
echo ""
echo "$ sudo ./omsagent_tsg"
echo ""