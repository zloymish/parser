<b>Выборочный парсер html</b>

Этот проект предназначен для того, чтобы обрабатывать html-файлы с заданными пользователем настройками.

Доступны 2 режима: текстовый и графический. 

В текстовом режиме программа обрабатывает html-файл и выводит всё текстовое содержимое в надлежащем виде в stdout. При этом соблюдаются переводы строк &lt;br&gt;, а также заменяются специальные символы вроде &amp;nbsp;

В графическом режиме программа обрабатывает html-файл, получает css-стили из вложенных в файл, а также загружает css-файлы и изображения из указанных ссылок. После этого, программа выводит в упрощённом виде обработанное содержимое на экран с соблюдением стилей и отображением картинок, используя графическую среду tkinter и модуль pillow.

В проекте также реализован фильтр содержимого по некоторым критериям (тег, атрибут, значение). Фильтр доступен эксклюзивный (blacklist) или инклюзивный (whitelist). Подробнее в разделе "Фильтр"

<b>Запуск программы и ввод пути</b>

Программа запускается из консоли. Перед названием программы необходимо написать python3. Самый простой вариант команды:

python3 parser.py

Такая команда запускает программу в графическом режиме без загрузки какой-либо страницы. Можно указать путь до файла сразу же в команде: -u для URL и -p для локального пути. Например:

python3 parser.py -u https://www.example.com/
python3 parser.py -p ../index.html

Вообще, локальный путь можно указать и как url, написав его как file:///"путь до файла"

Если указать u или p как ключ, но не указывать никакого пути, программа отправит в stdout текст о том, как правильно вводить команду.

Путь также можно указать в графическом интерфейсе. В верхней его части расположено поле для ввода, в которое можно ввести url.

Некоторые настройки также задаются с помощью ключей:
t - активирует текстовый режим
f - активирует фильтр (по умолчанию режим эксклюзивный)
e - эксклюзивный режим фильтра
i - инклюзивный режим фильтра

<b>Фильтр</b>

Как было сказано раннее, в программе есть фильтр, и у него есть 2 режима.
Фильтр применяется к 3 категориям: теги, атрибуты, значения атрибутов.
Ключевые слова, а также режим, если он не был указан в ключах, загружаются из файла filter.txt, если такой существует. Если его нет, фильтр отключается.

Файл filter.txt построен следующим образом: сначала идёт название в одной строке, начинающееся с #, а после идёт одно из 3 слов: "method:", "tags:" или "attributes:". В следующих строках указаны либо метод (inclusive/exclusive), либо теги в 1 строку через пробел, либо в разные строки атрибут, двоеточие и значения через пробел.

Если в filter.txt отсутствуют разделы tags или attributes, то фильтр для этих категорий считается выключенным.

В эксклюзивном режиме фильтра программа отбрасывает всё содержимое, которое соответствует фильтру. В инклюзивном наоборот, программа оставляет только то, что соответствует фильтру.

<b>Замена специальных символов</b>

Программа заменяет специальные символы на их соответствия из файла specSyms.txt. Если такого нет, программа не заменяет специальные символы.