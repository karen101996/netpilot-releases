# RAVLAN Security Policy

[English](#english) · [Русский](#русский) · [O‘zbekcha](#ozbekcha)

> [!IMPORTANT]
> **SSH encrypts network traffic. Telnet does not.** Local password encryption cannot make a Telnet connection secure.

## English

### Security model

RAVLAN is a Windows command-line utility for SSH and Telnet access. Credentials and device settings are stored locally, under the current Windows user profile.

| Local file | Purpose |
|---|---|
| `%USERPROFILE%\TelnetManager\credentials.json` | Encrypted Telnet credentials |
| `%USERPROFILE%\TelnetManager\ssh_passwords.json` | Encrypted SSH passwords |
| `%USERPROFILE%\TelnetManager\ssh_known_hosts` | Trusted SSH server host keys |

**Password protection:** RAVLAN uses Windows **DPAPI** to encrypt saved passwords at rest. DPAPI is tied to the Windows user context. It does not protect against malware running with the same user's privileges or compromise of that account.

**SSH:** SSH encrypts the connection. On first contact with an unknown host key, RAVLAN asks for confirmation and displays a fingerprint. Verify the fingerprint through a trusted channel before accepting it. Unexpected changes to previously trusted keys must be investigated.

**Telnet:** Telnet transmits login credentials and session data without transport encryption. Use Telnet only on trusted, isolated management networks, and prefer SSH whenever available.

**Updates:** RAVLAN retrieves update files over HTTPS and checks them against Git blob SHA-1 hashes in the public [version manifest](version.json). This verifies consistency with that manifest, **not authenticity through a digital signature**. Compromise of the repository or manifest is not independently prevented by this mechanism. Signed releases remain a future improvement.

**Privacy:** RAVLAN does not intentionally upload saved device passwords to GitHub. GitHub receives normal network requests when the application checks for or downloads updates.

### Reporting a vulnerability

**Do not disclose working exploits, credentials, private IP addresses, internal network diagrams or device configurations in public issues.**

For non-sensitive security questions or ordinary bugs, use [GitHub Issues](https://github.com/karen101996/ravlan-releases/issues). For sensitive vulnerabilities, use a private reporting option offered by the repository (if enabled) or contact the maintainer privately through an available verified channel. If no private channel is available, do not post exploit details publicly.

### Supported versions

Only the latest published stable release is intended for ongoing support. Older versions may not receive security fixes.

---

## Русский

### Модель безопасности

**RAVLAN** — консольная утилита для Windows, работающая с SSH и Telnet. Учётные данные и настройки устройств хранятся **локально**, в профиле текущего пользователя Windows.

| Локальный файл | Назначение |
|---|---|
| `%USERPROFILE%\TelnetManager\credentials.json` | Зашифрованные учётные данные Telnet |
| `%USERPROFILE%\TelnetManager\ssh_passwords.json` | Зашифрованные пароли SSH |
| `%USERPROFILE%\TelnetManager\ssh_known_hosts` | Доверенные ключи SSH-серверов |

**Шифрование паролей.** RAVLAN использует **Windows DPAPI** для защиты сохранённых паролей на диске. Шифрование привязано к контексту пользователя Windows, но не защищает от вредоносных программ, работающих с правами этого пользователя, или компрометации его учётной записи.

**Безопасность SSH.** SSH шифрует сетевой трафик. При первом подключении к неизвестному серверу RAVLAN показывает отпечаток ключа и запрашивает подтверждение. **Перед подтверждением проверь отпечаток ключа по доверенному источнику.** Неожиданная смена ранее сохранённого ключа требует проверки.

**Ограничения Telnet.** Telnet **не шифрует логин, пароль и содержимое сессии**. Даже зашифрованный на компьютере пароль передаётся через Telnet без защиты. Используй Telnet только в доверенной изолированной сети управления. Если оборудование поддерживает SSH, предпочтительнее использовать его.

**Обновления.** Файлы скачиваются через HTTPS и проверяются по Git blob SHA-1, указанным в публичном [манифесте версий](version.json). Такая проверка подтверждает соответствие файлов манифесту, **но не заменяет цифровую подпись** и не защищает независимо от компрометации репозитория или манифеста.

**Конфиденциальность.** RAVLAN не предназначен для отправки сохранённых паролей оборудования в GitHub. При проверке и скачивании обновлений GitHub получает обычные сетевые запросы.

### Как сообщить об уязвимости

**Не публикуй в открытых Issues** пароли, токены, реальные данные внутренней сети, конфигурации устройств или подробные инструкции по эксплуатации уязвимости.

Для обычных ошибок и несекретных вопросов используй [GitHub Issues](https://github.com/karen101996/ravlan-releases/issues). Для серьёзной уязвимости используй приватную форму сообщения GitHub, если она включена, либо другой подтверждённый приватный канал связи с сопровождающим проекта. Если приватного канала нет, не публикуй детали эксплуатации публично.

### Поддерживаемые версии

Поддержка безопасности предполагается для **последней опубликованной стабильной версии**. Более старые версии могут не получать исправлений.

---

## O‘zbekcha

### Xavfsizlik modeli

**RAVLAN** — Windows uchun SSH va Telnet orqali ulanish dasturi. Qurilmalarning hisob ma’lumotlari va sozlamalari Windows foydalanuvchisi profilida **mahalliy** saqlanadi.

| Mahalliy fayl | Vazifasi |
|---|---|
| `%USERPROFILE%\TelnetManager\credentials.json` | Shifrlangan Telnet hisob ma’lumotlari |
| `%USERPROFILE%\TelnetManager\ssh_passwords.json` | Shifrlangan SSH parollari |
| `%USERPROFILE%\TelnetManager\ssh_known_hosts` | Ishonchli SSH server kalitlari |

**Parollarni himoyalash.** Saqlangan parollar **Windows DPAPI** yordamida shifrlanadi. Bu ularni diskda himoyalaydi, ammo shu foydalanuvchi huquqlari bilan ishlayotgan zararli dasturlardan yoki foydalanuvchi hisobining buzib kirilishidan to‘liq himoya qilmaydi.

**SSH xavfsizligi.** SSH tarmoq trafigini shifrlaydi. Noma’lum serverga birinchi marta ulanganda RAVLAN server kalitining barmoq izini ko‘rsatib, tasdiqlashni so‘raydi. **Tasdiqlashdan oldin kalitni ishonchli manba orqali tekshiring.** Oldin saqlangan kalitning kutilmagan o‘zgarishini albatta tekshirish kerak.

**Telnet cheklovlari.** Telnet login, parol va sessiya ma’lumotlarini **shifrlamasdan uzatadi**. Kompyuterda shifrlangan parol ham Telnet orqali yuborilganda himoyasiz bo‘ladi. Telnet’dan faqat ishonchli, ajratilgan boshqaruv tarmoqlarida foydalaning. Imkon bo‘lsa, SSH’ni tanlang.

**Yangilanishlar.** Fayllar HTTPS orqali yuklab olinadi va ochiq [versiya manifestidagi](version.json) Git blob SHA-1 xeshlariga solishtiriladi. Bu faylning manifestga mosligini tekshiradi, ammo **raqamli imzo o‘rnini bosmaydi** va repozitoriy buzilgan taqdirda mustaqil himoya bermaydi.

**Maxfiylik.** RAVLAN saqlangan qurilma parollarini GitHub’ga yuborish uchun mo‘ljallanmagan. Yangilanishlarni tekshirish va yuklab olishda GitHub odatiy tarmoq so‘rovlarini qabul qiladi.

### Zaiflik haqida xabar berish

**Ommaviy Issues bo‘limiga** parollar, tokenlar, ichki tarmoq manzillari, qurilma konfiguratsiyalari yoki zaiflikdan foydalanishning batafsil ko‘rsatmalarini joylamang.

Oddiy xatoliklar va maxfiy bo‘lmagan savollar uchun [GitHub Issues](https://github.com/karen101996/ravlan-releases/issues) dan foydalaning. Jiddiy xavfsizlik zaifligi haqida xabar berish uchun, agar mavjud bo‘lsa, GitHub’ning maxfiy xabar berish funksiyasidan yoki loyiha egasi bilan tasdiqlangan shaxsiy aloqa kanalidan foydalaning. Maxfiy kanal mavjud bo‘lmasa, zaiflik tafsilotlarini ommaga chiqarmang.

### Qo‘llab-quvvatlanadigan versiyalar

Xavfsizlik yangilanishlari asosan **eng so‘nggi barqaror reliz** uchun mo‘ljallangan. Eski versiyalar tuzatishlarni olmasligi mumkin.
