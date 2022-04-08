# TCP/UDP scanner
Скрипт представляет собой сканер портов в заданном диапозоне, сообщая информацию о закрытых и открытых TCP/UDP портах.

# Установка
**Склонируйте репозиторий на свой компьютер.**

# Использование 
usage: TCP/UDP Scanner [-a ADDRESS] [-t PROTOCOL_TYPE] [-r RANGE_PORT] [-n THREAD_NUMBER]

Чтобы узнать подробную информацию, о том как пользоваться скриптом, передайте в качестве аргумента -h

# Примеры использования:
```ports_scanner.py -a 127.0.0.1 -t TCP -r 410:445 -n 300```

![image](https://user-images.githubusercontent.com/70903393/162487414-67590cea-b0fe-4612-9691-7dec13321c37.png)

`ports_scanner.py -a localhost -t UDP -r 100:130 -n 300`

![image](https://user-images.githubusercontent.com/70903393/162487779-75e96a40-4387-41d3-8461-2860ca59a17c.png)
