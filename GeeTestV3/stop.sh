kill -9 `lsof -i:8158      |awk '{print \$2}'|grep -o '[0-9]*'|sort -u`
