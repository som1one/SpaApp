import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_ru.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('ru')
  ];

  /// Название приложения
  ///
  /// In ru, this message translates to:
  /// **'SPA Salon'**
  String get appTitle;

  /// Заголовок экрана настроек
  ///
  /// In ru, this message translates to:
  /// **'Настройки'**
  String get settings;

  /// Секция общих настроек
  ///
  /// In ru, this message translates to:
  /// **'Общие настройки'**
  String get generalSettings;

  /// Переключатель уведомлений
  ///
  /// In ru, this message translates to:
  /// **'Уведомления'**
  String get notifications;

  /// Пункт поддержки
  ///
  /// In ru, this message translates to:
  /// **'Поддержка'**
  String get support;

  /// Подзаголовок поддержки
  ///
  /// In ru, this message translates to:
  /// **'Свяжитесь с нами'**
  String get contactUs;

  /// Секция внешнего вида
  ///
  /// In ru, this message translates to:
  /// **'Внешний вид'**
  String get appearance;

  /// Заголовок темы
  ///
  /// In ru, this message translates to:
  /// **'Тема'**
  String get theme;

  /// Светлая тема
  ///
  /// In ru, this message translates to:
  /// **'Светлая'**
  String get light;

  /// Темная тема
  ///
  /// In ru, this message translates to:
  /// **'Темная'**
  String get dark;

  /// Секция языка
  ///
  /// In ru, this message translates to:
  /// **'Язык'**
  String get language;

  /// Заголовок языка приложения
  ///
  /// In ru, this message translates to:
  /// **'Язык приложения'**
  String get appLanguage;

  /// Русский язык
  ///
  /// In ru, this message translates to:
  /// **'Русский'**
  String get russian;

  /// Английский язык
  ///
  /// In ru, this message translates to:
  /// **'English'**
  String get english;

  /// Секция безопасности
  ///
  /// In ru, this message translates to:
  /// **'Безопасность'**
  String get security;

  /// Биометрическая авторизация
  ///
  /// In ru, this message translates to:
  /// **'Биометрическая авторизация'**
  String get biometricAuth;

  /// Подзаголовок биометрической авторизации
  ///
  /// In ru, this message translates to:
  /// **'Вход по отпечатку или Face ID'**
  String get biometricAuthSubtitle;

  /// Секция дополнительно
  ///
  /// In ru, this message translates to:
  /// **'Дополнительно'**
  String get additional;

  /// О приложении
  ///
  /// In ru, this message translates to:
  /// **'О приложении'**
  String get aboutApp;

  /// Политика конфиденциальности
  ///
  /// In ru, this message translates to:
  /// **'Политика конфиденциальности'**
  String get privacyPolicy;

  /// Условия использования
  ///
  /// In ru, this message translates to:
  /// **'Условия использования'**
  String get termsOfUse;

  /// Очистить кэш
  ///
  /// In ru, this message translates to:
  /// **'Очистить кэш'**
  String get clearCache;

  /// Закрыть
  ///
  /// In ru, this message translates to:
  /// **'Закрыть'**
  String get close;

  /// Отмена
  ///
  /// In ru, this message translates to:
  /// **'Отмена'**
  String get cancel;

  /// Очистить
  ///
  /// In ru, this message translates to:
  /// **'Очистить'**
  String get clear;

  /// Версия приложения
  ///
  /// In ru, this message translates to:
  /// **'Версия {version}'**
  String version(String version);

  /// Подтверждение очистки кэша
  ///
  /// In ru, this message translates to:
  /// **'Вы уверены, что хотите очистить кэш?'**
  String get clearCacheConfirm;

  /// Кэш очищен
  ///
  /// In ru, this message translates to:
  /// **'Кэш очищен'**
  String get cacheCleared;

  /// Главная
  ///
  /// In ru, this message translates to:
  /// **'Главная'**
  String get home;

  /// Меню
  ///
  /// In ru, this message translates to:
  /// **'Меню'**
  String get menu;

  /// Записи
  ///
  /// In ru, this message translates to:
  /// **'Записи'**
  String get bookings;

  /// Профиль
  ///
  /// In ru, this message translates to:
  /// **'Профиль'**
  String get profile;

  /// Лояльность
  ///
  /// In ru, this message translates to:
  /// **'Лояльность'**
  String get loyalty;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'ru'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'ru':
      return AppLocalizationsRu();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
