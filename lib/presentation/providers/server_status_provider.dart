import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/config/app_config.dart';

enum ServerStatus { checking, available, unavailable }

class ServerStatusNotifier extends StateNotifier<ServerStatus> {
  ServerStatusNotifier() : super(ServerStatus.checking) {
    _wake();
  }

  // Dedicated Dio instance — no auth interceptors, so we get clean connection results.
  final _dio = Dio(BaseOptions(
    baseUrl: AppConfig.baseUrl,
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
