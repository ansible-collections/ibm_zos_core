# ==============================================================================
# Copyright (c) IBM Corporation 2023
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# ==============================================================================
# Mount data sets to USS mounts
# ==============================================================================

set -A mount_list "/zoau/v1.2.0:IMSTESTU.ZOAU.V120.ZFS" \
"/zoau/v1.0.0-ga:IMSTESTU.ZOAU.V100.GA.ZFS" \
"/zoau/v1.0.1-ga:IMSTESTU.ZOAU.V101.GA.ZFS" \
"/zoau/v1.0.1-ptf1:IMSTESTU.ZOAU.V101.PTF1.ZFS" \
"/zoau/v1.0.1-ptf2:IMSTESTU.ZOAU.V101.PTF2.ZFS" \
"/zoau/v1.0.2-ga:IMSTESTU.ZOAU.V102.GA.ZFS" \
"/zoau/v1.0.3-ga5:IMSTESTU.ZOAU.V103.GA5.ZFS" \
"/zoau/v1.0.3-ptf2:IMSTESTU.ZOAU.V103.PTF2.ZFS" \
"/zoau/v1.1.0-spr:IMSTESTU.ZOAU.V110.SPRINT.ZFS" \
"/zoau/v1.1.0-spr5:IMSTESTU.ZOAU.V1105.SPRINT.ZFS" \
"/zoau/v1.1.0-spr7:IMSTESTU.ZOAU.V1107.SPRINT.ZFS" \
"/zoau/v1.1.0-ga:IMSTESTU.ZOAU.V110.GA.ZFS" \
"/zoau/v1.1.1-ptf1:IMSTESTU.ZOAU.V111.PTF1.ZFS" \
"/zoau/v1.2.0f:IMSTESTU.ZOAU.V120F.ZFS" \
"/zoau/v1.2.1:IMSTESTU.ZOAU.V121.ZFS" \
"/zoau/v1.2.1-rc1:IMSTESTU.ZOAU.V121.RC1.ZFS" \
"/zoau/v1.2.1g:IMSTESTU.ZOAU.V121G.ZFS" \
"/zoau/v1.2.1h:IMSTESTU.ZOAU.V121H.ZFS" \
"/zoau/v1.2.2:IMSTESTU.ZOAU.V122.ZFS" \
"/zoau/latest:IMSTESTU.ZOAU.LATEST.ZFS" \
"/python:IMSTESTU.PYZ.ROCKET.V362B.ZFS" \
"/python2:IMSTESTU.PYZ.V380.GA.ZFS" \
"/python3:IMSTESTU.PYZ.V383PLUS.ZFS" \
"/allpython/3.10:IMSTESTU.PYZ.V3A0.ZFS" \
"/allpython/3.11:IMSTESTU.PYZ.V3B0.ZFS" \
"/allpython/3.11-ga:IMSTESTU.PYZ.V311GA.ZFS"

mount(){
    unset path
    unset data_set
    for tgt in "${mount_list[@]}" ; do
        # TODO: Can use something like the below to find ouf a mount is in place and act on that
        # df /zoau/v1.0.0-ga | tail -n +2 |cut -d " " -f 2 | sed 's/(//' | sed 's/.$//'
        path=`echo "${tgt}" | cut -d ":" -f 1`
        data_set=`echo "${tgt}" | cut -d ":" -f 2`
        mkdir -p ${path}
        echo "Mouting data set ${data_set} to ${path}."
        /usr/sbin/mount -r -t zfs -f ${data_set} ${path}
    done
}

unmount(){
    unset path
    unset data_set
    for tgt in "${mount_list[@]}" ; do
        path=`echo "${tgt}" | cut -d ":" -f 1`
        data_set=`echo "${tgt}" | cut -d ":" -f 2`
        echo "Unmounting data set ${data_set} from ${path}."
        /usr/sbin/unmount ${path}
    done
}

usage () {
	echo ""
	echo "Usage: $0 --mount, --unmount"
    echo "    $0 --mount"
	echo "Choices:"
	echo "  - mount: will create paths and mount data sets."
	echo "  - unmount: will unmount data sets from paths."
}

################################################################################
# Main arg parse
################################################################################
case "$1" in
--mount)
    mount
    ;;
--unmount)
    unmount
    ;;
*)
    usage
    ;;
esac
