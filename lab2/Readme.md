# Инструкция по использованию

Собираем и запускаем образ.

``` 
sudo docker build -t main && sudo docker run -i -t main 
```

Вызываем скрипт
``` 
python3.10 main.py --host google.com
```