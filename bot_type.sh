if [ $# -lt 1 ]; then
  echo "Usage: $0 \"要輸入文字\""
  exit 1
fi
TEXT="$1"
printf "%s\n" "$TEXT" >message.txt
scp message.txt welly@192.168.66.14:message.txt
ssh welly@192.168.66.14 'type.bat'
rm message.txt
