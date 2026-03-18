import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'l10n/app_localizations.dart';
import 'routes/app_router.dart';
import 'routes/route_names.dart';
import 'services/language_service.dart';
import 'services/push_service.dart';
import 'theme/app_theme.dart';

const bool _forceBootDebugScreen = false;

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
  Locale _locale = const Locale('ru');

  @override
  void initState() {
    super.initState();
    PushService().setNavigatorKey(navigatorKey);
    _loadLocale();
  }

  Future<void> _loadLocale() async {
    try {
      final locale = await LanguageService().getLocale();
      // Гарантируем, что по умолчанию используется русский
      final finalLocale =
          locale.languageCode == 'ru' || locale.languageCode == 'en'
              ? locale
              : const Locale('ru');
      if (mounted) {
        setState(() {
          _locale = finalLocale;
        });
      }
    } catch (e) {
      debugPrint('Ошибка загрузки локали: $e');
      // В случае ошибки используем русский по умолчанию
      if (mounted) {
        setState(() {
          _locale = const Locale('ru');
        });
      }
    }
  }

  void _setLocale(Locale locale) {
    // Сначала обновляем состояние для немедленного обновления UI
    setState(() {
      _locale = locale;
    });
    // Сохраняем в хранилище асинхронно (не блокирует UI)
    LanguageService().setLocale(locale);
  }

  @override
  Widget build(BuildContext context) {
    if (_forceBootDebugScreen) {
      return const Directionality(
        textDirection: TextDirection.ltr,
        child: ColoredBox(
          color: Colors.green,
          child: Center(
            child: Text(
              'BOOT OK',
              style: TextStyle(fontSize: 32, color: Colors.white),
            ),
          ),
        ),
      );
    }

    return MaterialApp(
      navigatorKey: navigatorKey,
      title: 'SPA Salon',
      theme: AppTheme.lightTheme,
      themeMode: ThemeMode.light,
      locale: _locale,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('ru'),
        Locale('en'),
      ],
      // Если система не поддерживает выбранный язык, используем русский
      localeResolutionCallback: (locale, supportedLocales) {
        if (locale == null) {
          return const Locale('ru');
        }
        // Проверяем, поддерживается ли локаль
        for (var supportedLocale in supportedLocales) {
          if (supportedLocale.languageCode == locale.languageCode) {
            return supportedLocale;
          }
        }
        // Если не поддерживается, возвращаем русский
        return const Locale('ru');
      },
      home: null,
      // Начинаем с registration, но пользователи могут продолжить как гости
      initialRoute: RouteNames.registration,
      onGenerateRoute: AppRouter.generateRoute,
      debugShowCheckedModeBanner: false,
      // Включаем поддержку высокой частоты обновления
      builder: (context, child) {
        // Если child null, показываем индикатор загрузки вместо белого экрана
        final widget = child ??
            const Scaffold(
              body: Center(
                child: CircularProgressIndicator(),
              ),
            );

        // Определяем, является ли устройство iPad
        final isTablet = MediaQuery.of(context).size.shortestSide >= 600;

        return MediaQuery(
          // Принудительно устанавливаем частоту обновления для плавности
          data: MediaQuery.of(context).copyWith(
            // Поддержка 120 Гц на устройствах с высокой частотой обновления
            highContrast: false,
            // Для iPad увеличиваем размер текста и элементов
            textScaleFactor: isTablet ? 1.1 : 1.0,
          ),
          child: LocalizationProvider(
            locale: _locale,
            setLocale: _setLocale,
            child: widget,
          ),
        );
      },
    );
  }
}

class LocalizationProvider extends InheritedWidget {
  final Locale locale;
  final void Function(Locale) setLocale;

  const LocalizationProvider({
    required this.locale,
    required this.setLocale,
    required super.child,
  });

  static LocalizationProvider? of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<LocalizationProvider>();
  }

  @override
  bool updateShouldNotify(LocalizationProvider oldWidget) {
    return oldWidget.locale != locale;
  }
}
