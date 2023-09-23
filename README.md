<h3 align="center">:gb: Disclaimer</h3>

:warning: This project is intended for use in a company with Russian-speaking
specialists. Therefore, all explanations, comments, and other texts are provided
in Russian only.

----

# :ru: Рефакторинг старого ПО (Visual Basic) на новый стек (Python) #

![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)
![Apache](https://img.shields.io/badge/apache-%23D42029.svg?style=plastic&logo=apache&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=plastic&logo=linux&logoColor=black)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=plastic&logo=ubuntu&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=plastic&logo=windows&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=plastic&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=plastic&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=plastic&logo=javascript&logoColor=%23F7DF1E)
**`JSON`**
**`PyQt5`**
**`PyPNG`**

----

### Исходное задание ###

- На сервере ПО OWEN собирает телеметрию с датчиков. Программа визуального
контроля запускается там же на сервере в единственном экземпляре, что требует
дополнительной RDP-сессии на АРМ дежурного персонала, и к тому же не позволяет
одновременный контроль с нескольких рабочих мест.
- Есть возможность некоторые температурные показания сбрасывать в файл
проприетарного формата OPR. Этот файл забирает VB-программа на единственную
рабочую станцию и выводит в отдельном окне с интервалом обновления около 20с.
- Для каждого измерения есть два пороговых значения для отображения цветового
предупреждения (yellow, red) и звуковой сигнализации, которые также хранятся в
отдельном конфигурационном файле, где можно изменять пороги.
- В графике отображается история измерений за определённый интервал времени
(например, за последний час)&nbsp;&mdash; некий аналог графиков в MRTG.
- Теперь надо отвязаться от ОС Windows и другого ПО Microsoft на рабочих
станциях, и ту же информацию выводить в окне браузера или платформонезависимого
приложения для одновременной работы на нескольких рабочих станциях без
необходимости установки излишнего ПО (VB-soft и некоторые модули от MS Access).
С алертами и музыкой. :wink:.
- Таким образом, по-прежнему надо забирать файлы с сетевого ресурса и потом уже
обрабатывать полученные данные.
- Поскольку всё происходит в среде Microsoft AD со строгими политиками,
доступных без авторизации сетевых шар нет. Поэтому рекомендуется создание
отдельной сервисной учётки для доступа куда надо.

### Варианты исполнения ###

Все варианты собраны в одном репозитории, чтобы было проще использовать
специалистам без глубоких знаний умностей типа Docker и CI/CD.

[**PoC (Proof of Concept)**](https://github.com/wildfielded/pro-owen/tree/master/PoC)
создан на стеке Python/Apache/Ubuntu. Отдельный `README.md` с инструкциями по
развёртыванию прилагается.

[**WebServer**](https://github.com/wildfielded/pro-owen/tree/master/WebServer)&nbsp;&mdash;
переработанный из **PoC** серверный вариант.

[**OwenCommon**](https://github.com/wildfielded/pro-owen/tree/master/OwenCommon)&nbsp;&mdash;
в модуле `common_func.py` собран функционал, общий для серверного и десктопного
вариантов.

[**Desktop WebView**](https://github.com/wildfielded/pro-owen/tree/master/WinWebView)
создан как desktop-приложение на основе наработок из **PoC**. Отдельный
`README.md` с инструкциями по развёртыванию прилагается.

[**OwenEmulator**](https://github.com/wildfielded/pro-owen/tree/master/OwenEmulator)
создан для имитации работы сервера OWEN исключительно для разработки при
отсутствии доступа к серверу. Создаёт на сетевом ресурсе точно такой же по
формату файл с данными телеизмерений, генерируемых некоторым случайным образом.

### TODO (ближайшие планы) ###

- Упрощение и автоматизация деплоя.
- Улучшайзинг кода и фиченаворотинг. Попытаться сделать код более оптимальным и
читабельным по мере прокачки экспы.

----
