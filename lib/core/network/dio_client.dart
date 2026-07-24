import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/app_config.dart';
import 'auth_storage.dart';

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: AppConfig.baseUrl,
    connectTimeout: const Duration(milliseconds: AppConfig.connectTimeoutMs),
    receiveTimeout: const Duration(milliseconds: AppConfig.receiveTimeoutMs),
    headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
  ));

  dio.interceptors.add(AuthInterceptor(dio, ref));
  dio.interceptors.add(LogInterceptor(requestBody: true, responseBody: true));

  return dio;
});

class AuthInterceptor extends Interceptor {
  final Dio _dio;
  final Ref _ref;

  AuthInterceptor(this._dio, this._ref);

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await AuthStorage.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      final refreshToken = await AuthStorage.getRefreshToken();
      if (refreshToken != null) {
        try {
          final response = await _dio.post('/auth/refresh', data: {'refresh_token': refreshToken});
          final data = response.data['data'];
          await AuthStorage.saveTokens(
            accessToken: data['access_token'],
            refreshToken: data['refresh_token'],
          );
          // Retry original request
          final opts = err.requestOptions;
          opts.headers['Authorization'] = 'Bearer ${data['access_token']}';
          final retry = await _dio.fetch(opts);
          return handler.resolve(retry);
        } catch (_) {
          await AuthStorage.clear();
        }
      }
    }
    handler.next(err);
  }
}
