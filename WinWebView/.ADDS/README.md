### Подготовка рабочей станции Windows для сборки проекта ###
- Понятно, что должен быть установлен Python, скачанный с [`python.org`](https://python.org).    
- Далее все требуемые пакеты устанавливаются через **`pip install pkgname`**.    
- Если **pip** не может пробиться через систему противоинтернетной обороны, надо
вручную скачивать последние версии пакетов (с возможными зависимостями) с
[`pypi.org`](https://pypi.org) и складывать в отдельную директорию, например
`D:\DIST`. Файлы **`.whl`** складывать как есть. Из архивов **`.zip`** и **`.tar.gz`**
распаковывать в `D:DIST` директории вида `pkgname-x.x.x`.    
- Например для установки **PySMB** скачать **`pysmb-x.x.x.zip`**, из него извлечь
в `D:DIST` папку **`pysmb-x.x.x`**. Дополнительно скачать и так же распаковать пакет
**`pyasn1-x.x.x.tar.gz`**. После этого уже можно дать команду:    
**`pip install --no-index --find-links="D:\DIST" PySMB`**    

----

Для установки **PyQt5** и зависимостей, используемых в текущем проекте, надо
действовать по аналогии, то есть скачать и выложить в `D:\DIST` следующие файлы
(или подобные):    
**`PyQt5-x.x.x-cp36-abi3-win_amd64.whl`**    
**`PyQt5_Qt5-x.x.x-py3-none-win_amd64.whl`**    
**`PyQt5_sip-x.x.x-cp310-cp310-win_amd64.whl`**    
**`PyQtWebEngine-x.x.x-cp36-win_amd64.whl`**    
**`PyQtWebEngine_Qt5-x.x.x-py3-none-win_amd64.whl`**    
В командной строке дать две команды:    
**`pip install --no-index --find-links="D:\DIST" PyQt5`**    
**`pip install --no-index --find-links="D:\DIST" PyQtWebEngine`**    

----

Для возможности собирать исполняемые файлы на рабочей станции с Windows, аналогично
понадобится целая коллекция файлов (искать по именам пакетов **pyinstaller**,
**pyinstaller-hooks-contrib**, **pywin32-ctypes**, **pefile**, **future**,
**altgraph**):    
**`pyinstaller-x.x-py3-none-win_amd64.whl`**    
**`pyinstaller_hooks_contrib-x.x-py2.py3-none-any.whl`**    
**`pywin32_ctypes-x.x.x-py2.py3-none-any.whl`**    
**`pefile-x.x.x.tar.gz`** (извлечь с помощью **7-zip** папку **`pefile-x.x.x`**)    
**`future-x.x.x.tar.gz`** (извлечь с помощью **7-zip** папку **`future-x.x.x`**)    
**`altgraph-x.x.x-py2.py3-none-any.whl`**    
И команда:    
**`pip install --no-index --find-links="D:\DIST" pyinstaller`**    

----

### Сборка owen.exe для установки на рабочие места дежурного персонала ###

На текущий момент можно делать так:    
- Скачать с репозитория zip-архив и распаковать например в D:\OWEN.    
- В command prompt перейти в D:\OWEN\WinWebView и скомандовать:    
**`pyinstaller main.py --name owen --onefile --icon icon-owen.ico --noconsole
--hidden-import ConfiGranit.py --hidden-import HTMLCreator.py`**    
- Готовый файл `owen.exe` находится в D:\OWEN\WinWebView\dist    
- Его скопировать в рабочую директорию, туда же положить все иконки, плюс
`owen.ini` и можно запускать.    
