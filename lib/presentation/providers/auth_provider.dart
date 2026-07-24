import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../core/network/auth_storage.dart';
import '../../core/network/dio_client.dart';

class AuthUser {
  final String id;
  final String email;
  final String? fullName;
  final String? avatarUrl;
  final String level;

  const AuthUser({required this.id, required this.email, this.fullName, this.avatarUrl, required this.level});

  factory AuthUser.fromJson(Map<String, dynamic> j) => AuthUser(
    id: j['id'] as String,
    email: j['email'] as String,
    fullName: j['full_name'] as String?,
    avatarUrl: j['avatar_url'] as String?,
    level: j['level'] as String? ?? 'beginner',
  );
}

class AuthState {
  final AuthUser? user;
  final bool isLoading;
  final String? error;

  const AuthState({this.user, this.isLoading = false, this.error});

  AuthState copyWith({AuthUser? user, bool? isLoading, String? error}) =>
      AuthState(user: user ?? this.user, isLoading: isLoading ?? this.isLoading, error: error);
}

class AuthNotifier extends StateNotifier<AuthState> {
  final Dio _dio;

  AuthNotifier(this._dio) : super(const AuthState()) {
    _loadMe();
  }

  Future<void> _loadMe() async {
    final token = await AuthStorage.getAccessToken();
    if (token == null) return;
    try {
      final res = await _dio.get('/auth/me');
      state = state.copyWith(user: AuthUser.fromJson(res.data['data'] as Map<String, dynamic>));
    } catch (_) {}
  }

  Future<void> login({required String email, required String password}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _dio.post('/auth/login', data: {'email': email, 'password': password});
      final data = res.data['data'] as Map<String, dynamic>;
      await AuthStorage.saveTokens(accessToken: data['access_token'] as String, refreshToken: data['refresh_token'] as String);
      await _loadMe();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: _parseError(e));
      rethrow;
    }
    state = state.copyWith(isLoading: false);
  }

  Future<void> register({required String email, required String password, String? fullName}) async {
    state = state.copyWith(isLoading: true);
    try {
      await _dio.post('/auth/register', data: {'email': email, 'password': password, 'full_name': fullName});
      await login(email: email, password: password);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: _parseError(e));
      rethrow;
    }
  }

  Future<void> logout() async {
    final rt = await AuthStorage.getRefreshToken();
    if (rt != null) {
      try { await _dio.post('/auth/logout', data: {'refresh_token': rt}); } catch (_) {}
    }
    await AuthStorage.clear();
    state = const AuthState();
  }

  String _parseError(Object e) {
    if (e is DioException) {
      return e.response?.data?['message'] as String? ?? e.message ?? 'Unknown error';
    }
    return e.toString();
  }
}

final authNotifierProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(dioProvider));
});
