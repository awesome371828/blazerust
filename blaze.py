import sys
import os
import shutil

from flask import Flask, render_template_string, abort
# -*- coding: utf-8 -*-
"""
BLAZE RUST — Wiki сайт сервера (Flask, один файл)

Запуск:
    pip install flask
    python blaze.py

Сайт откроется по адресу: http://127.0.0.1:5000
"""

from flask import Flask, render_template_string, abort

app = Flask(__name__)

ONLINE = 6
SERVER_IP = "play.blazerust.ru:28015"
DISCORD = "https://discord.gg/blazerust"

# ---------------------------------------------------------------------------
# Структура навигации
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Правила", [
        ("rules-intro", "Вводные правила"),
        ("rules-main", "Основные правила"),
        ("donate", "Соглашение на донат"),
    ]),
    ("Для новичков", [
        ("info-start", "Как начать"),
        ("info-privileges", "Привилегии и VIP"),
        ("info-commands", "Команды чата"),
        ("info-clans", "Как создать клан"),
    ]),
    ("Поддержка", [
        ("support-complaint", "Как подать жалобу"),
        ("support-punishments", "Наказания"),
    ]),
    ("Инструкции", [
        ("info-steamid", "Как узнать SteamID"),
        ("info-connect", "Подключение connect"),
    ]),
]

FLAT = [slug for _, items in SECTIONS for slug, _ in items]


def find_cat(slug):
    for cat, items in SECTIONS:
        for s, _ in items:
            if s == slug:
                return cat
    return ""


# ---------------------------------------------------------------------------
# Помощники разметки
# ---------------------------------------------------------------------------
def related(items):
    cards = "".join(
        '<a class="related-card reveal" href="/page/%s"><small>Читать далее</small>%s</a>'
        % (slug, title)
        for slug, title in items
    )
    return '<div class="related"><h3>Похожие статьи</h3><div class="related-grid">%s</div></div>' % cards


def callout(kind, title, text):
    return '<div class="callout %s reveal"><div><b>%s</b><p>%s</p></div></div>' % (kind, title, text)


def pager(slug):
    idx = FLAT.index(slug)
    prev_s = FLAT[idx - 1] if idx > 0 else None
    next_s = FLAT[idx + 1] if idx < len(FLAT) - 1 else None
    out = '<div class="pager">'
    if prev_s:
        out += '<a class="pager-btn prev reveal" href="/page/%s"><span>← Назад</span><strong>%s</strong></a>' % (
            prev_s, PAGES[prev_s]["title"])
    if next_s:
        out += '<a class="pager-btn next reveal" href="/page/%s"><span>Далее →</span><strong>%s</strong></a>' % (
            next_s, PAGES[next_s]["title"])
    out += "</div>"
    return out


# ---------------------------------------------------------------------------
# Контент страниц
# ---------------------------------------------------------------------------
PAGES = {}

PAGES["rules-intro"] = {
    "title": "Вводные правила",
    "html": '''
<p class="lead">Базовые положения проекта BLAZE RUST. Прочитай их до первого захода — это поможет избежать недопониманий и спорных ситуаций.</p>

<h2>Общие положения</h2>
<div class="list">
  <div class="li reveal"><span class="li-num">01</span><div><strong>Незнание правил не освобождает от ответственности</strong><p>Заходя на сервер BLAZE RUST, вы автоматически соглашаетесь с правилами проекта в полном объёме. Ознакомьтесь с ними заранее.</p></div></div>
  <div class="li reveal"><span class="li-num">02</span><div><strong>Решение администрации окончательно</strong><p>В спорных ситуациях окончательное решение остаётся за администрацией проекта. Спорные моменты, не описанные в правилах, трактуются на усмотрение администрации.</p></div></div>
  <div class="li reveal"><span class="li-num">03</span><div><strong>Правила могут изменяться</strong><p>Администрация вправе дополнять и изменять правила без отдельного оповещения. Актуальная версия всегда опубликована здесь, в BLAZE.wiki.</p></div></div>
  <div class="li reveal"><span class="li-num">04</span><div><strong>Все обращения — через Discord</strong><p>Жалобы, споры и вопросы решаются через создание тикета в нашем Discord. Доказательства (видео/скриншоты) повышают шанс на положительное решение.</p></div></div>
</div>
''' + callout("tip", "Совет", "После вводных правил обязательно прочитайте основные правила — именно за их нарушение выдаются блокировки.")
    + related([("rules-main", "Основные правила"), ("support-punishments", "Наказания"), ("donate", "Соглашение на донат")]),
}

PAGES["rules-main"] = {
    "title": "Основные правила",
    "html": '''
<p class="lead">Свод правил поведения на сервере BLAZE RUST. За их нарушение администрация вправе выдать предупреждение, мут или блокировку без возврата средств.</p>

<h2>Поведение и честная игра</h2>
<div class="list">
  <div class="li reveal"><span class="li-num">01</span><div><strong>Читы и стороннее ПО запрещены</strong><p>Использование читов, макросов, скриптов и любого ПО, дающего преимущество, — перманентный бан без возможности обжалования и возврата доната.</p></div></div>
  <div class="li reveal"><span class="li-num">02</span><div><strong>Эксплойты и баги</strong><p>Использование игровых багов и эксплойтов (дюп, проход сквозь текстуры и т.п.) запрещено. О найденных багах сообщайте администрации через Discord.</p></div></div>
  <div class="li reveal"><span class="li-num">03</span><div><strong>Обман администрации</strong><p>Попытка ввести администрацию в заблуждение, поддельные доказательства и обман при разборе жалоб караются блокировкой.</p></div></div>
</div>

<h2>Общение и чат</h2>
<div class="list">
  <div class="li reveal"><span class="li-num">04</span><div><strong>Уважение к игрокам</strong><p>Оскорбления, разжигание межнациональной розни, угрозы и травля в чате и голосовых каналах запрещены.</p></div></div>
  <div class="li reveal"><span class="li-num">05</span><div><strong>Спам и реклама</strong><p>Флуд, спам, капс и реклама сторонних проектов и услуг в чате запрещены.</p></div></div>
  <div class="li reveal"><span class="li-num">06</span><div><strong>Никнейм</strong><p>Запрещены оскорбительные, провокационные и вводящие в заблуждение никнеймы (в т.ч. имитация администрации).</p></div></div>
</div>
''' + callout("danger", "Важно", "Игровые действия (рейды, обманы внутри игры, союзы и предательства) — это часть Rust и не являются нарушением. Правила выше касаются поведения вне игровой механики.")
    + related([("rules-intro", "Вводные правила"), ("support-punishments", "Наказания"), ("support-complaint", "Как подать жалобу")]),
}

PAGES["donate"] = {
    "title": "Соглашение на донат",
    "html": '''
<p class="lead">Условия пополнения донат-счёта и возврата средств в магазине BLAZE RUST. Принимаются автоматически при пополнении баланса.</p>
''' + callout("note", "Автоматическое соглашение", "Пополняя свой баланс в магазине, вы автоматически принимаете условия этого раздела в полном объёме.")
    + '''
<h2>Содержание</h2>
<div class="grid grid-2">
  <div class="card tilt reveal"><div class="card-ico">01</div><h3>Пополнение счёта</h3><p>Правила пополнения донат-счёта и выдачи покупок.</p></div>
  <div class="card tilt reveal"><div class="card-ico">02</div><h3>Возврат средств</h3><p>Условия возврата и требования к видео-фиксации.</p></div>
</div>

<h2>Глава 1 · Пополнение счёта</h2>
<div class="list">
  <div class="li reveal"><span class="li-num">01</span><div><strong>Полное согласие</strong><p>Пополняя донат-счёт в нашем магазине, вы принимаете все правила проекта и соглашаетесь с ними в полном объёме.</p></div></div>
  <div class="li reveal"><span class="li-num">02</span><div><strong>Проблемы с товаром</strong><p>В случае возникновения проблем с купленными предметами мы обязаны решить все ваши проблемы. Компенсация выдаётся по усмотрению администратора.</p></div></div>
  <div class="li reveal"><span class="li-num">03</span><div><strong>Утеря данных</strong><p>При утере данных от аккаунта гарантия восстановления средств не предоставляется.</p></div></div>
  <div class="li reveal"><span class="li-num">04</span><div><strong>Обман администрации</strong><p>При попытке обмануть администрацию ваш счёт будет заморожен и аннулирован.</p></div></div>
  <div class="li reveal"><span class="li-num">05</span><div><strong>Нарушение правил</strong><p>За нарушение правил проекта администрация вправе лишить вас купленного доната.</p></div></div>
  <div class="li reveal"><span class="li-num">06</span><div><strong>Ошибочная покупка</strong><p>Если вы купили что-то по ошибке, но ещё не забрали из корзины (/store) — мы поможем восстановить баланс и заберём товар. Для этого достаточно создать тикет в Discord.</p></div></div>
</div>

<h2>Глава 2 · Возврат средств</h2>
<p>Средства возвращаются на банковский счёт по усмотрению администратора. В основном же их можно вернуть на донат-счёт и воспользоваться повторно для покупки товаров.</p>
<p><strong>Что считается браком:</strong> брак — это дефект, из-за которого продукция не может быть использована по своему назначению. Вы можете потребовать возврат, если у товара имеется брак.</p>
<p>Если у купленного товара возникает брак с новой функцией, добавленной на сервера в течение недели, — возврат не оформляется, а мы занимаемся исправлением. Если по истечении времени проблема осталась, возврат возможен.</p>

<h2>Чтобы получить возврат на счёт, нужна видео-фиксация:</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Момент пополнения счёта</h3><p>Запись должна начинаться с момента пополнения баланса.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Момент покупки товара</h3><p>Далее фиксируется сама покупка в магазине.</p></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Момент взятия товара из корзины</h3><p>Показываем выдачу товара через /store.</p></div></div>
  <div class="step reveal"><div class="step-num">4</div><div><h3>Сам «брак» товара</h3><p>И демонстрация дефекта. Видео должно быть цельным и не отредактированным.</p></div></div>
</div>
<p>Если видео-фиксация есть — создайте тикет в Discord, обратитесь к администратору и договоритесь, куда отправить запись для восстановления денежных средств.</p>
''' + callout("warn", "Возникла проблема?", "Все вопросы по донату и возврату решаются через тикет в Discord.")
    + related([("info-privileges", "Привилегии и VIP"), ("rules-main", "Основные правила"), ("info-commands", "Команды чата")]),
}

PAGES["support-complaint"] = {
    "title": "Как подать жалобу",
    "html": '''
<p class="lead">Жалобы на читеров и нарушителей рассматриваются через тикет в Discord. Чем полнее доказательства — тем быстрее решение.</p>

<h2>Как подать</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Создайте тикет в Discord</h3><p>Зайдите в наш Discord и откройте тикет в канале жалоб.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Укажите данные</h3><p>Сообщите ник и SteamID нарушителя, сервер и время нарушения.</p></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Приложите доказательства</h3><p>Прикрепите видео или скриншоты, где чётко видно нарушение. Дождитесь ответа администрации.</p></div></div>
</div>

<h2>Что приложить к жалобе</h2>
<div class="grid grid-3">
  <div class="card tilt reveal"><div class="card-ico">👤</div><h3>Ник и SteamID нарушителя</h3><p>Точные данные игрока, на которого подаёте жалобу.</p></div>
  <div class="card tilt reveal"><div class="card-ico">🎥</div><h3>Видео-доказательство</h3><p>Цельная, не отредактированная запись, где видно сам факт нарушения (чит, эксплойт, оскорбление).</p></div>
  <div class="card tilt reveal"><div class="card-ico">📅</div><h3>Дата, время и сервер</h3><p>Когда и на каком из серверов произошло нарушение.</p></div>
</div>
''' + callout("warn", "Без доказательств жалоба не рассматривается", "Голословные обвинения без видео или скриншотов администрация не принимает. Требования к видео-фиксации совпадают с разделом «Соглашение на донат».")
    + related([("support-punishments", "Наказания"), ("rules-main", "Основные правила"), ("info-commands", "Команды чата")]),
}

PAGES["support-punishments"] = {
    "title": "Наказания",
    "html": '''
<p class="lead">Ориентировочная таблица наказаний за нарушение правил. Окончательная мера определяется администрацией с учётом тяжести и повторности.</p>

<h2>Таблица наказаний</h2>
<div class="table-wrap"><table>
<thead><tr><th>Нарушение</th><th>Первое</th><th>Повторное</th></tr></thead>
<tbody>
<tr><td>Использование читов</td><td><span class="tag bad">Бан навсегда</span></td><td><span class="tag bad">Бан навсегда</span></td></tr>
<tr><td>Использование багов / эксплойтов</td><td><span class="tag mid">Бан 7 дней</span></td><td><span class="tag bad">Бан навсегда</span></td></tr>
<tr><td>Оскорбления в чате</td><td><span class="tag ok">Мут 1 час</span></td><td><span class="tag mid">Мут 24 часа</span></td></tr>
<tr><td>Спам / реклама</td><td><span class="tag ok">Предупреждение</span></td><td><span class="tag mid">Мут 12 часов</span></td></tr>
<tr><td>Обман администрации</td><td><span class="tag mid">Бан 3 дня</span></td><td><span class="tag bad">Бан навсегда</span></td></tr>
</tbody></table></div>
''' + callout("note", "Сроки ориентировочны", "Конкретная мера остаётся на усмотрение администрации и может быть строже при отягчающих обстоятельствах. Бан за читы обжалованию и возврату доната не подлежит.")
    + related([("rules-intro", "Вводные правила"), ("rules-main", "Основные правила"), ("support-complaint", "Как подать жалобу")]),
}

PAGES["info-start"] = {
    "title": "Как начать",
    "html": '''
<p class="lead">Пошаговый гайд для новичков: как скачать пиратку Rust, подключиться к BLAZE RUST и сделать первые шаги.</p>

<h2>Шаг 1. Скачай пиратку Rust</h2>
<p>Сервер BLAZE RUST полностью пиратский — лицензия не нужна. Скачай пиратскую версию Rust с проверенного источника, установи и запусти лаунчер.</p>

<h2>Шаг 2. Подключись к серверу</h2>
<p>Скопируй адрес сервера и вставь его в игровую консоль (клавиша F1):</p>
<div class="codeblock">connect play.blazerust.ru:28015</div>

<h2>Шаг 3. Начни выживать</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Собери базу</h3><p>Скорость добычи x10/x50 — фундамент и стены появятся за считанные минуты.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Забери киты</h3><p>Введи /kit в чате и получи стартовый набор.</p></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Объединяйся</h3><p>Создай клан через /clan create Название и зови друзей.</p></div></div>
</div>
''' + callout("tip", "Совет", "Перед первым заходом прочитай вводные и основные правила — это сэкономит нервы и сохранит донат.")
    + related([("info-connect", "Подключение connect"), ("info-commands", "Команды чата"), ("rules-intro", "Вводные правила")]),
}

PAGES["info-privileges"] = {
    "title": "Привилегии и VIP",
    "html": '''
<p class="lead">Привилегии дают доступ к уникальным возможностям: киты, телепорты, свои зоны и многое другое. Все покупки — через /store.</p>

<div class="grid grid-3">
  <div class="price-card tilt reveal">
    <h3>VIP</h3>
    <div class="price">149 ₽</div>
    <ul>
      <li>Кит VIP каждые 24 часа</li>
      <li>/sethome ×3</li>
      <li>Приоритет в очереди</li>
      <li>Цветной ник в чате</li>
    </ul>
    <a class="btn btn-ghost btn-sm" href="/page/donate">Купить</a>
  </div>
  <div class="price-card hot tilt reveal">
    <h3>PREMIUM</h3>
    <div class="price">349 ₽</div>
    <ul>
      <li>Всё из VIP</li>
      <li>Кит PREMIUM каждые 12 часов</li>
      <li>/sethome ×6, /tpa без кулдауна</li>
      <li>Своя зона на базе (2×2)</li>
    </ul>
    <a class="btn btn-primary btn-sm" href="/page/donate">Купить</a>
  </div>
  <div class="price-card tilt reveal">
    <h3>LEGENDARY</h3>
    <div class="price">699 ₽</div>
    <ul>
      <li>Всё из PREMIUM</li>
      <li>Кит LEGENDARY каждые 6 часов</li>
      <li>/sethome ×10, приватные ТП</li>
      <li>Особый скин и эффекты</li>
    </ul>
    <a class="btn btn-ghost btn-sm" href="/page/donate">Купить</a>
  </div>
</div>
''' + callout("note", "Выдача", "Все привилегии выдаются мгновенно через /store. При возникновении проблем создайте тикет в Discord.")
    + related([("donate", "Соглашение на донат"), ("info-commands", "Команды чата"), ("info-start", "Как начать")]),
}

PAGES["info-commands"] = {
    "title": "Команды чата",
    "html": '''
<p class="lead">Основные команды чата на BLAZE RUST. Пиши их в игровом чате (Enter) или в консоли (F1).</p>

<h2>Основные команды</h2>
<div class="table-wrap"><table>
<thead><tr><th>Команда</th><th>Описание</th></tr></thead>
<tbody>
<tr><td><span class="cmd-mini">/store</span></td><td>Открыть магазин и забрать покупки</td></tr>
<tr><td><span class="cmd-mini">/kit</span></td><td>Забрать доступные киты</td></tr>
<tr><td><span class="cmd-mini">/sethome</span></td><td>Установить точку дома</td></tr>
<tr><td><span class="cmd-mini">/home</span></td><td>Телепортироваться домой</td></tr>
<tr><td><span class="cmd-mini">/tpa &lt;ник&gt;</span></td><td>Запросить телепорт к игроку</td></tr>
<tr><td><span class="cmd-mini">/clan</span></td><td>Управление кланом</td></tr>
<tr><td><span class="cmd-mini">/w &lt;ник&gt; &lt;текст&gt;</span></td><td>Личное сообщение</td></tr>
<tr><td><span class="cmd-mini">/report &lt;ник&gt;</span></td><td>Пожаловаться на игрока</td></tr>
<tr><td><span class="cmd-mini">/top</span></td><td>Топ игроков</td></tr>
<tr><td><span class="cmd-mini">/stats</span></td><td>Твоя статистика</td></tr>
</tbody></table></div>
''' + callout("tip", "Подсказка", "Полный список команд смотри в игре через /help. По вопросам команд — тикет в Discord.")
    + related([("info-clans", "Как создать клан"), ("info-start", "Как начать"), ("info-privileges", "Привилегии и VIP")]),
}

PAGES["info-clans"] = {
    "title": "Как создать клан",
    "html": '''
<p class="lead">Клановая система на BLAZE RUST позволяет объединяться в группы, иметь общий дом и захватывать карту вместе.</p>

<h2>Как создать клан</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Создай клан</h3><p>Введи команду:</p><div class="cmd"><code>/clan create Название</code></div></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Пригласи друзей</h3><p>Отправь приглашение игроку:</p><div class="cmd"><code>/clan invite Ник</code></div></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Прими заявку</h3><p>Игрок принимает приглашение:</p><div class="cmd"><code>/clan accept</code></div></div></div>
</div>

<h2>Основные команды клана</h2>
<div class="table-wrap"><table>
<thead><tr><th>Команда</th><th>Описание</th></tr></thead>
<tbody>
<tr><td><span class="cmd-mini">/clan create &lt;название&gt;</span></td><td>Создать клан</td></tr>
<tr><td><span class="cmd-mini">/clan invite &lt;ник&gt;</span></td><td>Пригласить игрока</td></tr>
<tr><td><span class="cmd-mini">/clan kick &lt;ник&gt;</span></td><td>Исключить игрока</td></tr>
<tr><td><span class="cmd-mini">/clan leave</span></td><td>Покинуть клан</td></tr>
<tr><td><span class="cmd-mini">/clan info</span></td><td>Информация о клане</td></tr>
<tr><td><span class="cmd-mini">/clan base</span></td><td>Телепорт на базу клана</td></tr>
</tbody></table></div>
''' + callout("note", "Лимиты", "Максимальный размер клана и правила нейтралитета уточняй на сервере или в Discord.")
    + related([("info-commands", "Команды чата"), ("info-start", "Как начать"), ("rules-main", "Основные правила")]),
}

PAGES["info-steamid"] = {
    "title": "Как узнать SteamID",
    "html": '''
<p class="lead">SteamID нужен для жалоб, покупок и обращения в поддержку. Узнать его можно прямо в игре за 10 секунд.</p>

<h2>Способ 1. Игровая консоль</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Открой консоль</h3><p>Нажми клавишу F1 в игре.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Введи команду</h3><p>Напиши в консоли:</p><div class="cmd"><code>status</code></div></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Скопируй SteamID</h3><p>В списке игроков найди себя и скопируй ID вида <code>STEAM_0:1:12345678</code>.</p></div></div>
</div>

<h2>Способ 2. Сторонние сервисы</h2>
<p>Зайди на сайт <strong>steamidfinder.com</strong>, вставь ссылку на профиль Steam и получи свой SteamID64 / SteamID.</p>
''' + callout("tip", "Совет", "Храни SteamID под рукой — он понадобится в тикете Discord при жалобах и возврате доната.")
    + related([("support-complaint", "Как подать жалобу"), ("info-connect", "Подключение connect"), ("donate", "Соглашение на донат")]),
}

PAGES["info-connect"] = {
    "title": "Подключение connect",
    "html": '''
<p class="lead">Подключение к BLAZE RUST занимает меньше минуты. Используй игровую консоль или добавь сервер в избранное.</p>

<h2>Адрес сервера</h2>
<div class="codeblock">connect play.blazerust.ru:28015</div>

<h2>Как подключиться</h2>
<div class="steps">
  <div class="step reveal"><div class="step-num">1</div><div><h3>Запусти Rust</h3><p>Открой пиратскую версию Rust и нажми F1, чтобы открыть консоль.</p></div></div>
  <div class="step reveal"><div class="step-num">2</div><div><h3>Вставь команду</h3><p>Вставь <code>connect play.blazerust.ru:28015</code> и нажми Enter.</p></div></div>
  <div class="step reveal"><div class="step-num">3</div><div><h3>Начинай выживать</h3><p>Дождись загрузки и отправляйся на пустошь!</p></div></div>
</div>
''' + callout("warn", "Ошибка Timed Out (EAC)?", "Отключи EAC/античит в лаунчере или перезапусти игру. Подробнее — в технических гайдах.")
    + related([("info-start", "Как начать"), ("info-steamid", "Как узнать SteamID"), ("info-commands", "Команды чата")]),
}

# ---------------------------------------------------------------------------
# Главная страница
# ---------------------------------------------------------------------------
HOME_HTML = '''
<section class="hero">
  <div class="hero-badge"><span class="pulse-dot"></span>Пиратский сервер Rust · Без лицензии</div>
  <h1 class="hero-title">BLAZE <span>RUST</span></h1>
  <div class="hero-tags">
    <span>X10/X50</span><span>NOLIMIT</span><span>CLANS</span><span>LOOT+</span>
  </div>
  <p class="hero-sub">Самый горячий пиратский сервер Rust: ускоренная добыча, безлимитные возможности, кланы и усиленный лут. Выживай, строй, рейдь — и забирай своё место под солнцем пустоши!</p>
  <div class="hero-cta">
    <a class="btn btn-primary" href="/page/info-start">🚀 Начать играть</a>
    <a class="btn btn-ghost" href="/page/rules-intro">📜 Правила</a>
    <a class="btn btn-ghost" href="/page/donate">🛒 Магазин</a>
  </div>
  <div class="hero-stats">
    <div class="stat"><b class="count" data-count="6">0</b><small>онлайн</small></div>
    <div class="stat"><b class="count" data-count="250">0</b><small>макс. игроков</small></div>
    <div class="stat"><b class="count" data-count="24">0</b><small>поддержка 24/7</small></div>
    <div class="stat"><b class="count" data-count="100">0</b><small>вайпы по графику</small></div>
  </div>
</section>

<section class="section">
  <h2 class="section-title reveal">Особенности сервера</h2>
  <p class="section-sub reveal">Всё, за что игроки любят BLAZE RUST.</p>
  <div class="grid grid-4">
    <div class="card tilt reveal"><div class="card-ico">⚡</div><h3>X10/X50</h3><p>Скорость добычи и крафта до x10–x50. Собери базу и снаряжение за один вечер.</p></div>
    <div class="card tilt reveal"><div class="card-ico">♾️</div><h3>NOLIMIT</h3><p>Никаких искусственных ограничений: строй где хочешь и сколько хочешь.</p></div>
    <div class="card tilt reveal"><div class="card-ico">⚔️</div><h3>CLANS</h3><p>Полноценная клановая система: создавай клан, зови друзей и захватывай карту.</p></div>
    <div class="card tilt reveal"><div class="card-ico">💎</div><h3>LOOT+</h3><p>Улучшенный лут в ящиках и на военных объектах. Дроп бьёт рекорды.</p></div>
  </div>
</section>

<section class="section">
  <h2 class="section-title reveal">Преимущества</h2>
  <div class="grid grid-3">
    <div class="card tilt reveal"><div class="card-ico">🛡️</div><h3>Античит</h3><p>Жёсткая борьба с читерами: баны без права обжалования и возврата доната.</p></div>
    <div class="card tilt reveal"><div class="card-ico">👮</div><h3>Администрация 24/7</h3><p>Активные админы онлайн, быстрые разборы жалоб через Discord.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🗓️</div><h3>Вайпы по расписанию</h3><p>Регулярные вайпы по понятному графику — следи за анонсами.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🛒</div><h3>Мгновенный магазин</h3><p>Покупки выдаются через /store без ожидания и очередей.</p></div>
    <div class="card tilt reveal"><div class="card-ico">💬</div><h3>Дружное сообщество</h3><p>Активный Discord, кланы, ивенты и конкурсы с призами.</p></div>
    <div class="card tilt reveal"><div class="card-ico">🚀</div><h3>Стабильный сервер</h3><p>Современное железо, без лагов и падений даже на пике онлайна.</p></div>
  </div>
</section>

<section class="section">
  <h2 class="section-title reveal">Как начать</h2>
  <div class="steps">
    <div class="step reveal"><div class="step-num">1</div><div><h3>Скачай пиратку Rust</h3><p>Лицензия не нужна — сервер полностью пиратский.</p></div></div>
    <div class="step reveal"><div class="step-num">2</div><div><h3>Подключись к серверу</h3><p>В консоли (F1) введи <code>connect play.blazerust.ru:28015</code>.</p></div></div>
    <div class="step reveal"><div class="step-num">3</div><div><h3>Выживай и побеждай</h3><p>Забирай киты, строй базу, собирай клан и доминируй на пустоши.</p></div></div>
  </div>
  <div class="hero-cta" style="margin-top:28px"><a class="btn btn-primary" href="/page/info-start">Подробная инструкция</a></div>
</section>

<section class="section">
  <h2 class="section-title reveal">Частые вопросы</h2>
  <div class="faq">
    <details class="reveal"><summary>Это пиратский сервер? Нужна лицензия?</summary><p>Да, сервер полностью пиратский. Лицензия не нужна — достаточно скачать пиратскую версию Rust и подключиться по адресу сервера.</p></details>
    <details class="reveal"><summary>Какие вайпы и когда?</summary><p>Вайпы проходят по расписанию, которое публикуется в нашем Discord и в разделе Wiki. Следи за обновлениями.</p></details>
    <details class="reveal"><summary>Как создать клан?</summary><p>Используй команду /clan create Название. Полная инструкция — в разделе «Как создать клан».</p></details>
    <details class="reveal"><summary>Где купить привилегию?</summary><p>В магазине через /store на сервере или на сайте. Выдача происходит мгновенно после оплаты.</p></details>
    <details class="reveal"><summary>Что делать, если заметил читера?</summary><p>Оставь жалобу в Discord через тикет с видео-доказательствами. Инструкция — в разделе «Как подать жалобу».</p></details>
  </div>
</section>
'''

# ---------------------------------------------------------------------------
# Шаблон сайта (дизайн + анимации)
# ---------------------------------------------------------------------------
BASE = '''
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="BLAZE RUST [ X10/X50 | NOLIMIT | CLANS | LOOT+ ] — пиратский сервер Rust. Правила, донат, наказания, инструкции.">
<title>{{ page_title }} — BLAZE RUST</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;800&family=Manrope:wght@400;500;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg0:#03141c;--bg1:#042230;--bg2:#063245;
  --card:rgba(9,42,54,.55);--card2:rgba(13,56,70,.4);
  --line:rgba(103,232,249,.16);--line2:rgba(103,232,249,.32);
  --cyan:#22d3ee;--aqua:#7ff0f5;--teal:#2dd4bf;--sky:#38bdf8;
  --text:#dbf6fd;--muted:#9cc7d4;
  --grad:linear-gradient(120deg,#22d3ee,#2dd4bf 50%,#38bdf8);
  --shadow:0 20px 50px rgba(3,40,52,.55);
  --radius:18px;
}
html{scroll-behavior:smooth}
body{font-family:'Manrope',sans-serif;background:var(--bg0);color:var(--text);min-height:100vh;overflow-x:hidden;line-height:1.6}
a{color:var(--cyan)}
code{font-family:'JetBrains Mono',monospace;color:var(--aqua);background:rgba(34,211,238,.1);padding:2px 7px;border-radius:7px;border:1px solid var(--line2);font-size:.92em}

/* ---------- фон ---------- */
.bg-fx{position:fixed;inset:0;z-index:-2;background:
  radial-gradient(1200px 600px at 80% -10%,rgba(34,211,238,.14),transparent 60%),
  radial-gradient(900px 500px at 0% 30%,rgba(45,212,191,.10),transparent 55%),
  radial-gradient(1000px 700px at 100% 80%,rgba(56,189,248,.10),transparent 55%),
  linear-gradient(180deg,var(--bg0),var(--bg1) 55%,var(--bg0))}
.bg-fx::before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(103,232,249,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(103,232,249,.045) 1px,transparent 1px);background-size:44px 44px;-webkit-mask-image:radial-gradient(ellipse at 50% 0%,#000 0%,transparent 75%);mask-image:radial-gradient(ellipse at 50% 0%,#000 0%,transparent 75%)}
.orb{position:fixed;border-radius:50%;filter:blur(90px);opacity:.5;z-index:-1;animation:float 18s ease-in-out infinite}
.o1{width:420px;height:420px;background:rgba(34,211,238,.35);top:-120px;right:-80px}
.o2{width:340px;height:340px;background:rgba(45,212,191,.3);bottom:-100px;left:-90px;animation-delay:-6s}
.o3{width:260px;height:260px;background:rgba(56,189,248,.28);top:40%;left:55%;animation-delay:-12s}
@keyframes float{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(30px,-40px) scale(1.08)}66%{transform:translate(-25px,25px) scale(.94)}}

/* ---------- шапка ---------- */
.topbar{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:14px;padding:12px 22px;background:rgba(4,28,38,.72);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}
.burger{display:grid;place-items:center;width:40px;height:40px;border-radius:12px;border:1px solid var(--line2);background:rgba(13,56,70,.4);color:var(--aqua);font-size:18px;cursor:pointer;transition:.25s}
.burger:hover{background:rgba(34,211,238,.15);border-color:var(--cyan)}
@media(min-width:1024px){.burger{display:none}}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--text);font-family:'Unbounded',sans-serif}
.logo-mark{width:38px;height:38px;display:grid;place-items:center;border-radius:12px;background:var(--grad);color:#03222c;font-weight:800;font-size:20px;box-shadow:0 0 22px rgba(34,211,238,.45);animation:pulseGlow 3s ease-in-out infinite}
@keyframes pulseGlow{0%,100%{box-shadow:0 0 14px rgba(34,211,238,.35)}50%{box-shadow:0 0 30px rgba(34,211,238,.65)}}
.logo-text{font-size:17px;letter-spacing:1px}
.logo-text span{color:var(--cyan);margin-left:4px}
.top-actions{margin-left:auto;display:flex;align-items:center;gap:12px}
.online-badge{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;border-radius:999px;border:1px solid var(--line2);background:rgba(13,56,70,.45);font-size:13px;font-weight:700;color:var(--aqua);white-space:nowrap}
.online-badge i{width:8px;height:8px;border-radius:50%;background:#34d399;box-shadow:0 0 0 0 rgba(52,211,153,.7);animation:ping 1.6s infinite}
@keyframes ping{0%{box-shadow:0 0 0 0 rgba(52,211,153,.7)}70%{box-shadow:0 0 0 9px rgba(52,211,153,0)}100%{box-shadow:0 0 0 0 rgba(52,211,153,0)}}

/* ---------- сайдбар ---------- */
.sidebar{position:fixed;top:0;left:0;bottom:0;width:272px;padding:84px 16px 24px;background:rgba(4,26,36,.85);backdrop-filter:blur(18px);border-right:1px solid var(--line);transform:translateX(-100%);transition:transform .35s cubic-bezier(.22,1,.36,1);z-index:60;overflow-y:auto}
body.nav-open .sidebar{transform:translateX(0)}
@media(min-width:1024px){.sidebar{transform:none}}
.overlay{position:fixed;inset:0;background:rgba(2,12,18,.6);backdrop-filter:blur(2px);opacity:0;pointer-events:none;transition:opacity .3s;z-index:55}
body.nav-open .overlay{opacity:1;pointer-events:auto}
@media(min-width:1024px){.overlay{display:none}}
.sidebar-head{font-family:'Unbounded',sans-serif;font-size:12px;letter-spacing:3px;color:var(--cyan);padding:6px 12px 10px;text-transform:uppercase}
.nav-cat{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin:18px 12px 6px;opacity:.75}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;margin:2px 0;border-radius:12px;color:var(--muted);text-decoration:none;font-size:14px;font-weight:600;border:1px solid transparent;transition:.25s}
.nav-item::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--cyan);opacity:0;transform:scale(0);transition:.25s}
.nav-item:hover{color:var(--text);background:rgba(34,211,238,.08);border-color:var(--line);transform:translateX(4px)}
.nav-item:hover::before{opacity:1;transform:scale(1)}
.nav-item.active{color:#04222c;background:var(--grad);border-color:transparent;box-shadow:0 8px 24px rgba(34,211,238,.35)}
.nav-item.active::before{opacity:0}

/* ---------- контент ---------- */
.content{margin-left:0;padding:34px 20px 60px;max-width:1120px;width:100%}
@media(min-width:1024px){.content{margin-left:272px;padding:44px 52px 80px}}

/* ---------- кнопки ---------- */
.btn{position:relative;overflow:hidden;display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:13px 26px;border-radius:14px;font-weight:800;font-size:14px;letter-spacing:.3px;text-decoration:none;cursor:pointer;border:none;transition:transform .25s,box-shadow .25s;font-family:inherit}
.btn-primary{background:var(--grad);color:#03222c;box-shadow:0 10px 30px rgba(34,211,238,.35)}
.btn-primary:hover{transform:translateY(-3px);box-shadow:0 16px 40px rgba(34,211,238,.5)}
.btn-ghost{background:rgba(13,56,70,.4);color:var(--aqua);border:1px solid var(--line2)}
.btn-ghost:hover{transform:translateY(-3px);background:rgba(34,211,238,.12);border-color:var(--cyan)}
.btn::after{content:"";position:absolute;top:0;left:-80%;width:50%;height:100%;background:linear-gradient(105deg,transparent,rgba(255,255,255,.5),transparent);transform:skewX(-20deg);transition:left .55s}
.btn:hover::after{left:130%}
.btn-sm{padding:9px 16px;font-size:13px;border-radius:11px}
.ripple{position:absolute;border-radius:50%;background:rgba(255,255,255,.45);transform:scale(0);animation:rip .65s ease-out forwards;pointer-events:none}
@keyframes rip{to{transform:scale(1);opacity:0}}

/* ---------- hero ---------- */
.hero{position:relative;text-align:center;padding:56px 10px 30px;animation:fadeUp .8s ease both}
.hero-badge{display:inline-flex;align-items:center;gap:9px;padding:8px 18px;border-radius:999px;border:1px solid var(--line2);background:rgba(13,56,70,.45);font-size:13px;font-weight:700;color:var(--aqua);margin-bottom:22px;backdrop-filter:blur(8px)}
.pulse-dot{width:8px;height:8px;border-radius:50%;background:#34d399;box-shadow:0 0 0 0 rgba(52,211,153,.7);animation:ping 1.6s infinite}
.hero-title{font-family:'Unbounded',sans-serif;font-size:clamp(40px,8vw,86px);font-weight:800;line-height:1.05;background:linear-gradient(120deg,#a5f3fc,#22d3ee 40%,#2dd4bf 65%,#7dd3fc);-webkit-background-clip:text;background-clip:text;color:transparent;background-size:200% auto;animation:gradShift 6s linear infinite;filter:drop-shadow(0 10px 30px rgba(34,211,238,.25))}
.hero-title span{color:var(--cyan)}
@keyframes gradShift{to{background-position:200% center}}
.hero-tags{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:22px 0 14px}
.hero-tags span{padding:7px 16px;border-radius:999px;border:1px solid var(--line2);background:rgba(34,211,238,.08);color:var(--aqua);font-size:13px;font-weight:800;letter-spacing:1px}
.hero-sub{max-width:640px;margin:0 auto 30px;color:var(--muted);font-size:17px}
.hero-cta{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;margin-bottom:44px}
.hero-stats{display:flex;flex-wrap:wrap;gap:16px;justify-content:center}
.stat{min-width:150px;padding:20px 24px;border-radius:var(--radius);border:1px solid var(--line);background:var(--card);backdrop-filter:blur(10px);transition:.3s}
.stat:hover{transform:translateY(-5px);border-color:var(--line2);box-shadow:var(--shadow)}
.stat b{display:block;font-family:'Unbounded',sans-serif;font-size:30px;color:var(--aqua)}
.stat small{color:var(--muted);font-size:12px;letter-spacing:1px;text-transform:uppercase}

/* ---------- секции и карточки ---------- */
.section{padding:34px 0}
.section-title{font-family:'Unbounded',sans-serif;font-size:clamp(22px,3.4vw,34px);margin-bottom:8px;background:linear-gradient(120deg,#e0f7fd,#7ff0f5);-webkit-background-clip:text;background-clip:text;color:transparent}
.section-sub{color:var(--muted);margin-bottom:28px}
.grid{display:grid;gap:18px}
.grid-2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.grid-3{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.grid-4{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.card{position:relative;padding:26px;border-radius:var(--radius);border:1px solid var(--line);background:var(--card);backdrop-filter:blur(12px);transition:transform .35s,box-shadow .35s,border-color .35s;overflow:hidden}
.card::before{content:"";position:absolute;inset:0;background:radial-gradient(400px 200px at 50% -20%,rgba(34,211,238,.16),transparent 70%);opacity:0;transition:opacity .35s}
.card:hover{transform:translateY(-8px);border-color:var(--line2);box-shadow:0 22px 50px rgba(3,40,52,.6),0 0 0 1px rgba(34,211,238,.12)}
.card:hover::before{opacity:1}
.card-ico{width:52px;height:52px;border-radius:14px;display:grid;place-items:center;font-size:24px;background:rgba(34,211,238,.12);border:1px solid var(--line2);margin-bottom:16px;transition:.35s}
.card:hover .card-ico{transform:scale(1.1) rotate(-6deg);background:var(--grad);box-shadow:0 8px 24px rgba(34,211,238,.4)}
.card h3{font-size:18px;margin-bottom:8px}
.card p{color:var(--muted);font-size:14px}

/* ---------- шаги ---------- */
.steps{display:grid;gap:16px}
.step{display:flex;gap:18px;padding:22px;border-radius:var(--radius);border:1px solid var(--line);background:var(--card);backdrop-filter:blur(10px);transition:.3s}
.step:hover{border-color:var(--line2);transform:translateX(8px)}
.step-num{flex:0 0 auto;width:46px;height:46px;border-radius:14px;display:grid;place-items:center;font-family:'Unbounded',sans-serif;font-weight:800;font-size:18px;background:var(--grad);color:#03222c;box-shadow:0 6px 18px rgba(34,211,238,.35)}
.step h3{font-size:17px;margin-bottom:4px}
.step p{color:var(--muted);font-size:14px}

/* ---------- callout ---------- */
.callout{padding:18px 22px;border-radius:14px;border:1px solid;margin:24px 0;display:flex;gap:14px;align-items:flex-start;animation:fadeUp .6s ease both}
.callout b{display:block;margin-bottom:2px}
.callout p{font-size:14px;opacity:.92;margin:0}
.callout.tip{background:rgba(45,212,191,.1);border-color:rgba(45,212,191,.35)}
.callout.tip b{color:#5eead4}
.callout.note{background:rgba(56,189,248,.1);border-color:rgba(56,189,248,.35)}
.callout.note b{color:#7dd3fc}
.callout.warn{background:rgba(251,191,36,.1);border-color:rgba(251,191,36,.35)}
.callout.warn b{color:#fcd34d}
.callout.danger{background:rgba(248,113,113,.1);border-color:rgba(248,113,113,.4)}
.callout.danger b{color:#fca5a5}

/* ---------- статья ---------- */
.article{animation:fadeUp .7s ease both}
.crumbs{display:flex;flex-wrap:wrap;gap:8px;font-size:13px;color:var(--muted);margin-bottom:14px}
.crumbs a{color:var(--cyan);text-decoration:none;transition:.2s}
.crumbs a:hover{text-shadow:0 0 12px rgba(34,211,238,.8)}
.page-title{font-family:'Unbounded',sans-serif;font-size:clamp(26px,4.6vw,44px);margin-bottom:10px;background:linear-gradient(120deg,#e0f7fd,#7ff0f5);-webkit-background-clip:text;background-clip:text;color:transparent}
.lead{color:var(--muted);font-size:16px;max-width:760px;margin-bottom:26px}
.article h2{font-family:'Unbounded',sans-serif;font-size:clamp(19px,2.6vw,26px);margin:36px 0 16px;display:flex;align-items:center;gap:12px}
.article h2::before{content:"";width:8px;height:28px;border-radius:99px;background:var(--grad);box-shadow:0 0 16px rgba(34,211,238,.6)}
.article h3{font-size:18px;margin:22px 0 10px;color:var(--aqua)}
.article p{color:#cdeaf3;margin-bottom:12px}

/* ---------- список-карточки ---------- */
.list{display:grid;gap:14px;margin:18px 0}
.li{display:flex;gap:16px;padding:18px 20px;border-radius:14px;border:1px solid var(--line);background:var(--card);transition:.3s}
.li:hover{border-color:var(--line2);transform:translateX(6px);background:var(--card2)}
.li-num{flex:0 0 auto;font-family:'Unbounded',sans-serif;color:var(--cyan);font-size:14px;padding-top:3px}
.li strong{display:block;margin-bottom:2px}
.li p{color:var(--muted);font-size:14px;margin:0}

/* ---------- таблицы ---------- */
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:16px;background:var(--card);backdrop-filter:blur(10px);margin:20px 0}
table{width:100%;border-collapse:collapse;min-width:520px}
th{font-family:'Unbounded',sans-serif;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;text-align:left;padding:16px 20px;color:var(--aqua);background:rgba(34,211,238,.08);border-bottom:1px solid var(--line2)}
td{padding:15px 20px;font-size:14px;border-bottom:1px solid var(--line);color:#cdeaf3}
tbody tr{transition:.2s}
tbody tr:hover{background:rgba(34,211,238,.07)}
tbody tr:last-child td{border-bottom:none}
.tag{display:inline-block;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:800}
.tag.bad{background:rgba(248,113,113,.15);color:#fca5a5;border:1px solid rgba(248,113,113,.4)}
.tag.mid{background:rgba(251,191,36,.12);color:#fcd34d;border:1px solid rgba(251,191,36,.35)}
.tag.ok{background:rgba(45,212,191,.12);color:#5eead4;border:1px solid rgba(45,212,191,.35)}
.cmd-mini{display:inline-block;padding:3px 10px;border-radius:8px;background:rgba(34,211,238,.1);border:1px solid var(--line2);font-family:'JetBrains Mono',monospace;font-size:12.5px;color:var(--aqua)}

/* ---------- команды / код ---------- */
.cmd{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:12px 18px;border-radius:12px;border:1px solid var(--line);background:rgba(2,20,28,.7);font-family:'JetBrains Mono',monospace;font-size:14px;color:#7ff0f5;margin:10px 0;transition:.25s}
.cmd:hover{border-color:var(--cyan);box-shadow:0 0 18px rgba(34,211,238,.2);transform:translateX(4px)}
.codeblock{background:rgba(2,20,28,.85);border:1px solid var(--line2);border-radius:14px;padding:16px 18px;font-family:'JetBrains Mono',monospace;font-size:14px;color:#7ff0f5;margin:14px 0;overflow-x:auto}

/* ---------- прайс-карточки ---------- */
.price-card{position:relative;padding:28px 24px;border-radius:20px;border:1px solid var(--line);background:var(--card);backdrop-filter:blur(12px);text-align:center;transition:.35s;overflow:hidden}
.price-card:hover{transform:translateY(-10px);border-color:var(--line2);box-shadow:0 24px 60px rgba(3,40,52,.65)}
.price-card.hot{border-color:rgba(34,211,238,.5);box-shadow:0 0 40px rgba(34,211,238,.18)}
.price-card .price{font-family:'Unbounded',sans-serif;font-size:30px;color:var(--aqua);margin:14px 0}
.price-card ul{list-style:none;text-align:left;margin:14px 0 20px;display:grid;gap:8px}
.price-card li{font-size:13.5px;color:var(--muted);display:flex;gap:8px;align-items:flex-start}
.price-card li::before{content:"✔";color:var(--teal);font-weight:800}

/* ---------- pager ---------- */
.pager{display:flex;justify-content:space-between;gap:14px;margin-top:44px;flex-wrap:wrap}
.pager-btn{flex:1;min-width:220px;padding:18px 22px;border-radius:16px;border:1px solid var(--line);background:var(--card);text-decoration:none;color:var(--muted);transition:.3s;display:block}
.pager-btn:hover{border-color:var(--cyan);transform:translateY(-4px);box-shadow:0 14px 34px rgba(3,40,52,.5);color:var(--text)}
.pager-btn span{font-size:12px;letter-spacing:1px;text-transform:uppercase;opacity:.8;display:block;margin-bottom:4px}
.pager-btn strong{color:var(--aqua);font-size:15px}
.pager-btn.next{text-align:right}

/* ---------- похожие статьи ---------- */
.related{margin-top:44px;padding-top:26px;border-top:1px solid var(--line)}
.related h3{font-family:'Unbounded',sans-serif;font-size:16px;color:var(--aqua);margin-bottom:14px;letter-spacing:1px}
.related-grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.related-card{display:block;padding:18px;border-radius:14px;border:1px solid var(--line);background:var(--card);text-decoration:none;color:var(--text);transition:.3s}
.related-card:hover{border-color:var(--cyan);transform:translateY(-5px);box-shadow:0 14px 30px rgba(3,40,52,.5)}
.related-card small{display:block;color:var(--cyan);font-size:12px;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px}

/* ---------- FAQ ---------- */
.faq details{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 22px;margin-bottom:12px;transition:.3s}
.faq details[open]{border-color:var(--cyan);box-shadow:0 10px 30px rgba(3,40,52,.5)}
.faq summary{cursor:pointer;font-weight:800;font-size:15.5px;display:flex;justify-content:space-between;align-items:center;gap:12px;list-style:none}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-size:22px;color:var(--cyan);transition:transform .3s}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq p{color:var(--muted);font-size:14px;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}

/* ---------- футер и анимации ---------- */
.footer{margin-left:0;padding:30px 24px 40px;text-align:center;color:var(--muted);font-size:13px;border-top:1px solid var(--line);background:rgba(3,22,30,.5)}
@media(min-width:1024px){.footer{margin-left:272px}}
.reveal{opacity:0;transform:translateY(28px);transition:opacity .7s ease,transform .7s ease}
.reveal.visible{opacity:1;transform:none}
@keyframes fadeUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
::-webkit-scrollbar{width:10px}
::-webkit-scrollbar-track{background:#04222c}
::-webkit-scrollbar-thumb{background:linear-gradient(#22d3ee,#2dd4bf);border-radius:99px}
::selection{background:rgba(34,211,238,.35)}
</style>
</head>
<body>
<div class="bg-fx"></div>
<div class="orb o1"></div>
<div class="orb o2"></div>
<div class="orb o3"></div>

<header class="topbar">
  <button class="burger" onclick="toggleSidebar()" aria-label="Меню">☰</button>
  <a class="logo" href="/"><span class="logo-mark">B</span><span class="logo-text">BLAZE<span>RUST</span></span></a>
  <div class="top-actions">
    <span class="online-badge"><i></i>{{ online }} online</span>
    <a class="btn btn-primary btn-sm" href="/page/donate">🛒 Магазин</a>
  </div>
</header>

<aside id="sidebar" class="sidebar">
  <div class="sidebar-head">Разделы Wiki</div>
  <nav>
    <a class="nav-item {{ 'active' if active == 'home' else '' }}" href="/">🏠 Главная</a>
    {% for cat, items in sections %}
      <div class="nav-cat">{{ cat }}</div>
      {% for slug, label in items %}
        <a class="nav-item {{ 'active' if active == slug else '' }}" href="/page/{{ slug }}">{{ label }}</a>
      {% endfor %}
    {% endfor %}
  </nav>
</aside>
<div class="overlay" onclick="toggleSidebar()"></div>

<main class="content">
  {{ content }}
</main>

<footer class="footer">© 2026 BLAZE RUST. Все права защищены. · Пиратский сервер Rust · <a href="/page/rules-intro">Правила</a> · <a href="/page/donate">Магазин</a></footer>

<script>
// появление при скролле
var revs = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, {threshold:.12});
  revs.forEach(function(r){ io.observe(r); });
} else {
  revs.forEach(function(r){ r.classList.add('visible'); });
}

// анимированные счётчики
var counts = document.querySelectorAll('.count');
var cio = new IntersectionObserver(function(es){
  es.forEach(function(e){
    if (!e.isIntersecting) return;
    var el = e.target;
    var target = +el.dataset.count;
    var cur = 0;
    var step = Math.max(1, Math.round(target/50));
    var t = setInterval(function(){
      cur += step;
      if (cur >= target) { cur = target; clearInterval(t); }
      el.textContent = cur;
    }, 28);
    cio.unobserve(el);
  });
}, {threshold:.5});
counts.forEach(function(c){ cio.observe(c); });

// 3D-наклон карточек
document.querySelectorAll('.tilt').forEach(function(card){
  card.addEventListener('mousemove', function(e){
    var r = card.getBoundingClientRect();
    var x = (e.clientX - r.left) / r.width - .5;
    var y = (e.clientY - r.top) / r.height - .5;
    card.style.transform = 'perspective(850px) rotateY(' + (x*7) + 'deg) rotateX(' + (-y*7) + 'deg) translateY(-6px)';
  });
  card.addEventListener('mouseleave', function(){ card.style.transform = ''; });
});

// волна-клик по кнопкам
document.addEventListener('click', function(e){
  var b = e.target.closest('.btn');
  if (!b) return;
  var r = b.getBoundingClientRect();
  var s = document.createElement('span');
  s.className = 'ripple';
  var size = Math.max(r.width, r.height);
  s.style.width = s.style.height = size + 'px';
  s.style.left = (e.clientX - r.left - size/2) + 'px';
  s.style.top = (e.clientY - r.top - size/2) + 'px';
  b.appendChild(s);
  setTimeout(function(){ s.remove(); }, 650);
});

// мобильное меню
function toggleSidebar(){ document.body.classList.toggle('nav-open'); }
</script>
</body>
</html>
'''


# ---------------------------------------------------------------------------
# Маршруты
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template_string(
        BASE,
        page_title="Главная",
        active="home",
        content=HOME_HTML,
        online=ONLINE,
        sections=SECTIONS,
    )


@app.route("/page/<slug>")
def wiki(slug):
    if slug not in PAGES:
        abort(404)
    info = PAGES[slug]
    cat = find_cat(slug)
    crumbs = '<nav class="crumbs"><a href="/">Главная</a><span>/</span><span>%s</span><span>/</span><span>%s</span></nav>' % (cat, info["title"])
    header = '<h1 class="page-title">%s</h1>' % info["title"]
    body = '<div class="article">%s%s%s%s</div>' % (crumbs, header, info["html"], pager(slug))
    return render_template_string(
        BASE,
        page_title=info["title"],
        active=slug,
        content=body,
        online=ONLINE,
        sections=SECTIONS,
    )


if __name__ == "__main__":
    print("BLAZE RUST Wiki запущен: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
