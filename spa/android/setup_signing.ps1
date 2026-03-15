# Скрипт для настройки подписи Android
# Запусти: powershell -ExecutionPolicy Bypass -File setup_signing.ps1

Write-Host "=== Настройка подписи Android для PRIRODA SPA ===" -ForegroundColor Green
Write-Host ""

# Проверяем, существует ли уже keystore
if (Test-Path "upload-keystore.jks") {
    Write-Host "WARNING: Keystore уже существует!" -ForegroundColor Yellow
    $overwrite = Read-Host "Перезаписать? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Отменено." -ForegroundColor Red
        exit
    }
    Remove-Item "upload-keystore.jks"
}

# Запрашиваем пароли
Write-Host "Введи пароли для keystore:" -ForegroundColor Cyan
$storePassword = Read-Host "Store Password (минимум 6 символов)" -AsSecureString
$storePasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($storePassword))

if ($storePasswordPlain.Length -lt 6) {
    Write-Host "ERROR: Пароль должен быть минимум 6 символов!" -ForegroundColor Red
    exit
}

$keyPassword = Read-Host "Key Password (или Enter для использования того же)" -AsSecureString
$keyPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($keyPassword))

if ($keyPasswordPlain.Length -eq 0) {
    $keyPasswordPlain = $storePasswordPlain
    Write-Host "Используется тот же пароль для key" -ForegroundColor Yellow
}

# Запрашиваем информацию о сертификате
Write-Host ""
Write-Host "Информация о сертификате:" -ForegroundColor Cyan
$nameInput = Read-Host -Prompt 'Имя и фамилия (CN) [PRIRODA SPA]'
$name = if ($nameInput) { $nameInput } else { "PRIRODA SPA" }

$orgUnitInput = Read-Host -Prompt 'Подразделение (OU) [Development]'
$orgUnit = if ($orgUnitInput) { $orgUnitInput } else { "Development" }

$orgInput = Read-Host -Prompt 'Организация (O) [PRIRODA SPA]'
$org = if ($orgInput) { $orgInput } else { "PRIRODA SPA" }

$cityInput = Read-Host -Prompt 'Город (L) [Moscow]'
$city = if ($cityInput) { $cityInput } else { "Moscow" }

$stateInput = Read-Host -Prompt 'Область/Регион (ST) [Moscow]'
$state = if ($stateInput) { $stateInput } else { "Moscow" }

$countryInput = Read-Host -Prompt 'Код страны (C, 2 буквы) [RU]'
$country = if ($countryInput) { $countryInput } else { "RU" }

# Создаем keystore
Write-Host ""
Write-Host "Создаю keystore..." -ForegroundColor Cyan

$keytoolArgs = @(
    "-genkey",
    "-v",
    "-keystore", "upload-keystore.jks",
    "-keyalg", "RSA",
    "-keysize", "2048",
    "-validity", "10000",
    "-alias", "upload",
    "-storepass", $storePasswordPlain,
    "-keypass", $keyPasswordPlain,
    "-dname", "CN=$name, OU=$orgUnit, O=$org, L=$city, ST=$state, C=$country"
)

try {
    $process = Start-Process -FilePath "keytool" -ArgumentList $keytoolArgs -NoNewWindow -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "SUCCESS: Keystore создан успешно!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Ошибка при создании keystore!" -ForegroundColor Red
        exit
    }
} catch {
    Write-Host "ERROR: keytool не найден. Убедись, что Java установлена и в PATH." -ForegroundColor Red
    Write-Host "   Установи Java JDK или Android Studio" -ForegroundColor Yellow
    exit
}

# Создаем key.properties
Write-Host ""
Write-Host "Создаю key.properties..." -ForegroundColor Cyan

$keyPropertiesContent = "storePassword=$storePasswordPlain`nkeyPassword=$keyPasswordPlain`nkeyAlias=upload`nstoreFile=../upload-keystore.jks"

if (Test-Path "key.properties") {
    Write-Host "WARNING: key.properties уже существует!" -ForegroundColor Yellow
    $overwrite = Read-Host "Перезаписать? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Отменено." -ForegroundColor Red
        exit
    }
}

$keyPropertiesContent | Out-File -FilePath "key.properties" -Encoding UTF8 -NoNewline

Write-Host "SUCCESS: key.properties создан!" -ForegroundColor Green

# Очищаем пароли из памяти
$storePasswordPlain = $null
$keyPasswordPlain = $null

Write-Host ""
Write-Host "=== Готово! ===" -ForegroundColor Green
Write-Host ""
Write-Host "SUCCESS: Keystore: android/upload-keystore.jks" -ForegroundColor Green
Write-Host "SUCCESS: Конфигурация: android/key.properties" -ForegroundColor Green
Write-Host ""
Write-Host "ВАЖНО:" -ForegroundColor Yellow
Write-Host "   - Сохрани keystore и пароли в безопасном месте!" -ForegroundColor Yellow
Write-Host "   - Без keystore нельзя обновлять приложение в Google Play!" -ForegroundColor Yellow
Write-Host "   - Эти файлы уже добавлены в .gitignore" -ForegroundColor Yellow
Write-Host ""
Write-Host "Теперь можно собрать release версию:" -ForegroundColor Cyan
Write-Host "  flutter build appbundle --release" -ForegroundColor White
