import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/config/app_config.dart';

enum ServerStatus { checking, available, unavailable }

class ServerStatusNotifier extends StateNotifier<ServerStatus> {
  ServerStatusNotifier() : super(ServerStatus.checking) {
    _wake();
  }

  // Always ping the real backend URL directly — AppConfig.baseUrl may be empty
  // if API_BASE_URL was not injected at compile time, which would give a false positive.
  static String get _pingBase {
    const configured = AppConfig.baseUrl;
    if (configured.isNotEmpty) return configured;
    return 'https://learn-5-by-5-api-backend.onrender.com/api/v1';
  }

  // Dedicated Dio instance — no auth interceptors, so we get clean connection results.
  late final _dio = Dio(BaseOptions(
    baseUrl: _pingBase,
    connectTimeout: const Duration(seconds: 12),
    receiveTimeout: const Duration(seconds: 12),
  ));

  static const int _maxAttempts = 5;
  static const Duration _retryDelay = Duration(seconds: 6);

  Future<void> _wake() async {
    state = ServerStatus.checking;
    for (int i = 0; i < _maxAttempts; i++) {
      try {
        // Any HTTP response (even 401/404) means the server is awake.
        await _dio.get(
          '/auth/me',
          options: Options(validateStatus: (_) => true),
        );
        state = ServerStatus.available;
        return;
      } on DioException catch (e) {
        final isConnErr = e.type == DioExceptionType.connectionError ||
            e.type == DioExceptionType.connectionTimeout;

        if (!isConnErr) {
          // Got an HTTP response → server is up.
          state = ServerStatus.available;
          return;
        }

        // Connection failed — retry after delay unless it's the last attempt.
        if (i < _maxAttempts - 1) {
          await Future.delayed(_retryDelay);
        }
      } catch (_) {
        if (i < _maxAttempts - 1) await Future.delayed(_retryDelay);
      }
    }
    state = ServerStatus.unavailable;
  }

  Future<void> retry() => _wake();
}

final serverStatusProvider =
    StateNotifierProvider<ServerStatusNotifier, ServerStatus>(
  (_) => ServerStatusNotifier(),
);
