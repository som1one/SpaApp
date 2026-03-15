class Validators {
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Пожалуйста, укажите адрес электронной почты';
    }

    final trimmed = value.trim();
    const allowedDomains = [
      'gmail.com',
      'yahoo.com',
      'yandex.ru',
      'yandex.com',
      'mail.ru',
      'icloud.com',
      'outlook.com',
      'hotmail.com',
      'bk.ru',
      'list.ru',
      'inbox.ru',
    ];

    final emailRegex = RegExp(
      r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
    );

    if (!emailRegex.hasMatch(trimmed)) {
      return 'Адрес выглядит неверно. Проверьте формат.';
    }

    final domain = trimmed.split('@').last.toLowerCase();
    if (!allowedDomains.contains(domain)) {
      return 'Почтовый домен $domain пока не поддерживается';
    }

    return null;
  }
  
  static String? validateRequired(String? value, String fieldName) {
    if (value == null || value.isEmpty) {
      return 'Пожалуйста, заполните поле $fieldName';
    }
    return null;
  }
  
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Пожалуйста, введите пароль';
    }
    
    if (value.length < 8) {
      return 'Пароль должен содержать минимум 8 символов';
    }

    if (!RegExp(r'[A-ZА-Я]').hasMatch(value)) {
      return 'Добавьте хотя бы одну заглавную букву';
    }

    if (!RegExp(r'\d').hasMatch(value)) {
      return 'Добавьте хотя бы одну цифру';
    }

    if (!RegExp(r'[^A-Za-z0-9]').hasMatch(value)) {
      return 'Добавьте хотя бы один специальный символ';
    }
    
    return null;
  }
  
  static String? validatePhone(String? value) {
    if (value == null || value.isEmpty) {
      return 'Пожалуйста, введите номер телефона';
    }
    
    final phoneRegex = RegExp(r'^\+?[0-9]{10,15}$');
    
    if (!phoneRegex.hasMatch(value.replaceAll(RegExp(r'[\s-]'), ''))) {
      return 'Введите корректный номер телефона';
    }
    
    return null;
  }
}

