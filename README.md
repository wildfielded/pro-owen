## Рефакторинг старого ПО (Visual Basic) на новый стек (Python) ##
### Исходное задание ###
- На сервере ПО OWEN собирает телеметрию с датчиков. Некоторые температурные
показания сбрасываются в файл проприетарного формата OPR. Этот файл забирает
VB-программа на единственную рабочую станцию дежурного персонала и выводит в
отдельном окне с интервалом обновления около 20с.    
- Для каждого измерения есть два пороговых значения для отображения цветового
предупреждения (yellow, red) и звуковой сигнализации, которые также хранятся в
отдельном конфигурационном файле, где можно изменять пороги.    
- В графике отображается история измерений за определённый интервал времени
(например, за последний час) - некий аналог графиков в MRTG.    
- Теперь надо ту же информацию выводить в окне браузера (чтобы можно было смотреть
с нескольких рабочих станций) без необходимости установки излишнего ПО (VB-soft
и некоторые модули от MS Access). С алертами и музыкой =)    
### Примерное ТЗ ###
1. Забрать по SMB/CIFS текстовый файл в кодировке Windows-1251, в котором построчно
(для каждого датчика) 4 поля, разделённых табами: EventDate (дата), EventTime
(время), Description (место датчика), Value (температура).    
2. Забрать по SMB/CIFS текстовый файл в кодировке Windows-1251, в котором построчно
(для каждого датчика) 3 поля, разделённые табами: Description (место датчика),
Max1 ("жёлтый" порог температуры), Max2 ("красный" порог температуры).    
3. Поступившие данные надо распарсить, выдать текущую температуру на web-page и
сохранить в истории.    
4. В истории хранить данные за определённый интервал времени. Устаревшие данные
удалять.    
5. Если показания датчика достигают пороговых значений, на web-page должны
происходить соответствующие раскраски. В идеале может вылетать модальное окно
плюс проигрываться страшные звуки тревоги.    
6. Датчики иногда сбоят и если нет данных больше минуты, то вместо цифр в файл
выдавётся **`?`**. Также сама программа иногда вылетает и перестаёт обновлять
файл на шаре. По этим случаям также предусмотреть аудиовизуальные алерты.
- [**Proof of Concept**](https://github.com/wildfielded/pet-owen/tree/master/PoC)
создаётся на стеке Python/Apache/Ubuntu. Соответственно, на Ubuntu помимо пакета
**`apache2`** требуется установка **`pipenv`** и потом из хранилища PyPI установка
**`pysmb`**.    
Поскольку всё происходит в среде Microsoft AD со строгими политиками, доступных
без авторизации сетевых шар нет. Поэтому рекомендуется создание отдельной
сервисной учётки для доступа куда надо.    
- Для MVP предполагается экспериментальная замена Apache на Bottle или Django.    
#### Done (что сделано) ####
- Забираем файлы измерений и порогов с сетевого ресурса к себе.    
- Генерилка простенького HTML c автообновлением. Выдача в таблицу местоположения
датчиков и температуры.    
- Работает на сервере с Apache.    
#### Добавки ####
[**`.ADDS`**](https://github.com/wildfielded/pet-owen/tree/master/.ADDS) - дополнительные
вещи и телодвижения для деплоя.    
#### Doing (ближайшие планы) ####
- Хранение истории измерений без привлечения каких-либо БД, обойтись форматом JSON.    
- Класс для данных каждого отдельного сенсора, в формате JSON, для хранения всех
данных и обмена ими между модулями.    
- Выдача данных в таблицу.    
- Нормальная генерилка HTML.    
#### ToDo (прекрасные мечты) ####
- Генерилка гистограмм    
