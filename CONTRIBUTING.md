# Contributing to NetPilot

[English](#english) · [Русский](#русский) · [O‘zbekcha](#ozbekcha)

Thank you for helping improve **NetPilot**, a Windows SSH and Telnet utility. Reports from real networking environments are especially valuable.

## English

### Bug reports and feature requests

Use [GitHub Issues](https://github.com/karen101996/netpilot-releases/issues) for non-sensitive bugs, compatibility feedback and feature requests. Please include:

1. **NetPilot version:** output of `np version`.
2. **System:** Windows version and terminal (CMD, PowerShell or Windows Terminal).
3. **Connection type:** SSH or Telnet; device vendor/model and firmware version if relevant.
4. **Reproduction steps:** commands you ran, expected behavior and what happened instead.
5. **Safe diagnostics:** error messages or console output with passwords, usernames, tokens, public/private IP addresses, hostnames, device configuration and other sensitive details removed.

A useful issue title is: `[SSH] Terminal input problem on <device model>`.

### Development and pull requests

This repository publishes NetPilot releases, installation scripts and update metadata. Active feature development and code review happen in a separate private repository. **Please open an issue before preparing a pull request** so we can confirm the appropriate contribution path. Do not post proprietary device configurations or credentials.

### Security reports

**Do not publish exploitable vulnerabilities or secrets in public issues.** See [Security Policy](SECURITY.md) for reporting guidance.

---

## Русский

Спасибо за помощь в развитии **NetPilot** — утилиты для подключения к сетевому оборудованию через SSH и Telnet в Windows.

### Как сообщить об ошибке

Создай обращение в разделе [GitHub Issues](https://github.com/karen101996/netpilot-releases/issues). Желательно указать:

1. **Версию NetPilot:** результат команды `np version`.
2. **Операционную систему:** версию Windows и используемый терминал (CMD, PowerShell или Windows Terminal).
3. **Тип подключения:** SSH или Telnet, производителя и модель оборудования, при необходимости версию прошивки.
4. **Как воспроизвести ошибку:** введённые команды, ожидаемый результат и фактическое поведение.
5. **Диагностику:** текст ошибки или вывод консоли **без паролей, логинов, токенов, IP-адресов, имён устройств и конфиденциальной конфигурации**.

Пример названия обращения: `[SSH] Не работает ввод команд на <модель устройства>`.

### Как предложить улучшение

Открой [новое обращение](https://github.com/karen101996/netpilot-releases/issues/new), опиши проблему, которую решит функция, и приведи пример желаемого поведения. Особенно полезны предложения, основанные на реальном опыте работы с MikroTik, коммутаторами, OLT и другим оборудованием.

### Участие в разработке

Этот публичный репозиторий используется для распространения установочных файлов, релизов и метаданных обновлений. Основная разработка и проверка кода ведутся в отдельном приватном репозитории. **Прежде чем отправлять Pull Request, создай Issue**, чтобы согласовать подход.

### Сообщения об уязвимостях

Не публикуй пароли, резервные копии конфигураций и подробности потенциально опасных уязвимостей в открытых обращениях. Порядок сообщения описан в [политике безопасности](SECURITY.md).

---

## O‘zbekcha

**NetPilot** — Windows uchun SSH va Telnet orqali tarmoq qurilmalariga ulanish dasturini rivojlantirishga yordam berganingiz uchun rahmat.

### Xatolik haqida xabar berish

[GitHub Issues](https://github.com/karen101996/netpilot-releases/issues) bo‘limida yangi murojaat yarating va quyidagilarni ko‘rsating:

1. **NetPilot versiyasi:** `np version` buyrug‘i natijasi.
2. **Tizim:** Windows versiyasi va ishlatilayotgan terminal (CMD, PowerShell yoki Windows Terminal).
3. **Ulanish turi:** SSH yoki Telnet, qurilma ishlab chiqaruvchisi va modeli, kerak bo‘lsa proshivka versiyasi.
4. **Xatoni takrorlash:** kiritilgan buyruqlar, kutilgan natija va amalda yuz bergan holat.
5. **Xavfsiz diagnostika:** parollar, loginlar, tokenlar, IP manzillar, qurilma nomlari va maxfiy konfiguratsiyalar olib tashlangan xato matni yoki konsol chiqishi.

Murojaat sarlavhasiga misol: `[SSH] <qurilma modeli> da buyruq kiritish muammosi`.

### Yangi imkoniyat taklif qilish

[GitHub Issues](https://github.com/karen101996/netpilot-releases/issues/new) orqali qanday muammoni hal qilmoqchi ekaningizni va yangi imkoniyat qanday ishlashi kerakligini tushuntiring. Haqiqiy tarmoq qurilmalari bilan ishlash tajribasiga asoslangan takliflar ayniqsa foydali.

### Loyihani rivojlantirish

Ushbu ochiq repozitoriy o‘rnatish fayllari, relizlar va yangilanish ma’lumotlarini tarqatish uchun mo‘ljallangan. Asosiy dasturlash va kodni tekshirish alohida yopiq repozitoriyda olib boriladi. **Pull Request yuborishdan oldin Issue yarating**, shunda taklifni kelishib olamiz.

### Xavfsizlik muammolari

Parollarni, qurilma konfiguratsiyasi nusxalarini yoki xavfli zaiflik tafsilotlarini ommaviy murojaatlarda e’lon qilmang. [Xavfsizlik siyosati](SECURITY.md) bilan tanishing.
