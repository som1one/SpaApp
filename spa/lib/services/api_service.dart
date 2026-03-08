import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../utils/constants.dart';
import '../utils/api_exceptions.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  String? _token;

  set token(String? value) {
    _token = value;
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Future<dynamic> get(String endpoint, {int maxRetries = 3}) async {
    return _executeWithRetry(
      () async {
        final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}$endpoint');
        final response = await http
            .get(url, headers: _headers)
            .timeout(AppConstants.connectionTimeout);
        return _handleResponse(response);
      },
      maxRetries: maxRetries,
    );
  }

  /// Выполнение запроса с автоматическим retry
  Future<T> _executeWithRetry<T>(
    Future<T> Function() request, {
    int maxRetries = 3,
    Duration retryDelay = const Duration(seconds: 1),
  }) async {
    int attempt = 0;
    Exception? lastException;

    while (attempt < maxRetries) {
      try {
        return await request();
      } on TimeoutException catch (e) {
        lastException = e;
        attempt++;
        if (attempt >= maxRetries) {
          throw TimeoutException(originalError: e);
        }
        await Future.delayed(retryDelay * attempt);
      } catch (e) {
        lastException = e is Exception ? e : Exception(e.toString());
        
        // Не повторяем для ошибок авторизации и валидации
        if (e is UnauthorizedException || 
            e is ForbiddenException || 
            e is ValidationException) {
          rethrow;
        }

        // SocketException доступен только на мобильных платформах
        if (!kIsWeb) {
          try {
            // Проверяем тип через runtimeType для избежания ошибок компиляции на веб
            final errorType = e.runtimeType.toString();
            if (errorType == 'SocketException' || errorType.contains('SocketException')) {
              attempt++;
              if (attempt >= maxRetries) {
                throw NetworkException(originalError: e);
              }
              await Future.delayed(retryDelay * attempt);
              continue;
            }
          } catch (_) {
            // Игнорируем, если SocketException недоступен
          }
        }

        if (e is http.ClientException) {
          attempt++;
          if (attempt >= maxRetries) {
            throw NetworkException(originalError: e);
          }
          await Future.delayed(retryDelay * attempt);
          continue;
        }

        if (e is ApiException) rethrow;
        
        attempt++;
        if (attempt >= maxRetries) {
          throw _mapToApiException(e);
        }
        await Future.delayed(retryDelay * attempt);
      }
    }

    throw lastException ?? UnknownException(message: 'Неизвестная ошибка');
  }

  Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic>? data, {
    bool throwOnError = true,
    int maxRetries = 3,
  }) async {
    return _executeWithRetry(
      () async {
        final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}$endpoint');
        final response = await http
            .post(
              url,
              headers: _headers,
              body: data != null ? jsonEncode(data) : null,
            )
            .timeout(AppConstants.connectionTimeout);

        try {
          return _handleResponse(response);
        } catch (e) {
          if (!throwOnError) {
            // При throwOnError=false возвращаем ответ даже при ошибке
            dynamic responseBody;
            try {
              responseBody = response.body.isNotEmpty 
                  ? json.decode(response.body) 
                  : {'message': 'Пустой ответ'};
            } catch (_) {
              responseBody = {'message': response.body.isNotEmpty ? response.body : 'Ошибка парсинга'};
            }
            return responseBody;
          }
          rethrow;
        }
      },
      maxRetries: maxRetries,
    );
  }

  Future<Map<String, dynamic>> put(
    String endpoint,
    Map<String, dynamic>? data, {
    int maxRetries = 3,
  }) async {
    return _executeWithRetry(
      () async {
        final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}$endpoint');
        final response = await http
            .put(
              url,
              headers: _headers,
              body: data != null ? jsonEncode(data) : null,
            )
            .timeout(AppConstants.connectionTimeout);
        return _handleResponse(response);
      },
      maxRetries: maxRetries,
    );
  }

  Future<Map<String, dynamic>> patch(
    String endpoint,
    Map<String, dynamic>? data, {
    int maxRetries = 3,
  }) async {
    return _executeWithRetry(
      () async {
        final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}$endpoint');
        final response = await http
            .patch(
              url,
              headers: _headers,
              body: data != null ? jsonEncode(data) : null,
            )
            .timeout(AppConstants.connectionTimeout);
        return _handleResponse(response);
      },
      maxRetries: maxRetries,
    );
  }

  Future<Map<String, dynamic>> delete(String endpoint, {int maxRetries = 3}) async {
    return _executeWithRetry(
      () async {
        final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}$endpoint');
        final response = await http
            .delete(url, headers: _headers)
            .timeout(AppConstants.connectionTimeout);
        return _handleResponse(response);
      },
      maxRetries: maxRetries,
    );
  }

  Future<Map<String, dynamic>> uploadFile(
    String endpoint,
    File file, {
    String fieldName = 'file',
    int maxRetries = 3,
  }) async {
    if (kIsWeb) {
      throw UnsupportedError('Загрузка файлов не поддерживается на веб-платформе');
    }

    return _executeWithRetry(
      () async {
        final url = Uri.parse('${AppConstants.baseUrl}${AppConstants.apiVersion}$endpoint');
        
        final request = http.MultipartRequest('POST', url);
        
        // Убираем Content-Type из headers для multipart запросов
        // MultipartRequest сам установит правильный Content-Type с boundary
        final headers = Map<String, String>.from(_headers);
        headers.remove('Content-Type');
        
        request.headers.addAll(headers);
        
        final fileStream = file.openRead();
        final fileLength = await file.length();
        final extension = file.path.split('.').last.toLowerCase();
        
        MediaType contentType;
        if (extension == 'jpg' || extension == 'jpeg') {
          contentType = MediaType('image', 'jpeg');
        } else if (extension == 'png') {
          contentType = MediaType('image', 'png');
        } else if (extension == 'webp') {
          contentType = MediaType('image', 'webp');
        } else {
          contentType = MediaType('image', 'jpeg'); // По умолчанию
        }
        
        final multipartFile = http.MultipartFile(
          fieldName,
          fileStream,
          fileLength,
          filename: file.path.split('/').last,
          contentType: contentType,
        );
        
        request.files.add(multipartFile);
        
        final streamedResponse = await request.send().timeout(AppConstants.connectionTimeout);
        final response = await http.Response.fromStream(streamedResponse);
        
        return _handleResponse(response);
      },
      maxRetries: maxRetries,
    );
  }

  dynamic _handleResponse(http.Response response) {
    final statusCode = response.statusCode;
    dynamic responseBody;
    
    // Валидация ответа
    if (response.body.isEmpty && statusCode >= 200 && statusCode < 300) {
      return {};
    }
    
    try {
      if (response.body.isNotEmpty) {
        responseBody = json.decode(response.body);
      } else {
        responseBody = {};
      }
    } catch (e) {
      // Если не JSON, возвращаем текст
      responseBody = {'message': response.body.isNotEmpty ? response.body : 'Пустой ответ от сервера'};
    }

    if (statusCode >= 200 && statusCode < 300) {
      return responseBody;
    }

    // Обработка ошибок по статус кодам
    String errorMessage = 'Ошибка сервера';
    Map<String, dynamic>? errors;

    if (responseBody is Map) {
      errorMessage = responseBody['detail'] ?? 
                     responseBody['message'] ?? 
                     responseBody['error'] ?? 
                     errorMessage;
      
      // Извлекаем ошибки валидации
      if (responseBody['errors'] != null) {
        errors = responseBody['errors'] as Map<String, dynamic>?;
      }
    }

    switch (statusCode) {
      case 400:
      case 422:
        throw ValidationException(
          message: errorMessage,
          errors: errors,
          statusCode: statusCode,
        );
      case 401:
        throw UnauthorizedException(
          message: errorMessage,
        );
      case 403:
        throw ForbiddenException(
          message: errorMessage,
        );
      case 404:
        throw NotFoundException(
          message: errorMessage,
        );
      case 500:
      case 502:
      case 503:
      case 504:
        throw ServerException(
          message: errorMessage,
          statusCode: statusCode,
        );
      default:
        throw ServerException(
          message: errorMessage,
          statusCode: statusCode,
        );
    }
  }

  /// Преобразует обычные исключения в ApiException
  ApiException _mapToApiException(dynamic error) {
    final errorString = error.toString().toLowerCase();
    
    if (errorString.contains('timeout')) {
      return TimeoutException(originalError: error);
    }
    
    if (errorString.contains('socketexception') ||
        errorString.contains('failed host lookup') ||
        errorString.contains('network is unreachable') ||
        errorString.contains('connection refused') ||
        errorString.contains('connection timed out')) {
      return NetworkException(originalError: error);
    }
    
    return UnknownException(
      message: getErrorMessage(error),
      originalError: error,
    );
  }
}

