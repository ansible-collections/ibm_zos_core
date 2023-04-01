
is_bash=false
# if [ "$is_bash" = true ]; then
#     echo "here"
#     declare -A MYARRAY=(["1.0.3:/zoau/v1.0.3-ptf2")
# else
#     typeset -A MYARRAY=(["key1"]=data1 ['key2']=data2 ['key3']=data3)
# fi

# echo ${MYARRAY[@]}

zoau=(
"1.0.3:/zoau/v1.0.3-ptf2"
"1.1.1:/zoau/v1.1.1-ptf1"
"1.2.0:/zoau/v1.2.0"
"1.2.1:/zoau/v1.2.1"
"1.2.2:/zoau/v1.2.2"
"B1.2.2:/global/zoautil/1.2.2"
)

# echo ${zoau[@]}

# for key in "${!MYARRAY[@]}";do
# echo "Key : $key - Value : ${MYARRAY[$key]}"; 
# done
is_bash=false
z="1.0.3:/zoau/v1.0.3-ptf2"\ " "\
"1.1.1:/zoau/v1.1.1-ptf1"\ " "\
"1.2.0:/zoau/v1.2.0"\ " "\
"1.2.1:/zoau/v1.2.1"\ " "\
"1.2.2:/zoau/v1.2.2"\ " "\
"B1.2.2:/global/zoautil/1.2.2"

arr()if [ "$is_bash" = true  ]; then
        # set -A $1 "${@:2}"
        set -A $1 "$z"
   else
        #eval $1='("${@:2}")'
        eval $1='("${@:2}")'
   fi

arr B $z

 echo ${B[@]}
 echo "zzz"
 #echo ${zoau[@]}



 