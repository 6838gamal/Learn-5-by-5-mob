import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../../core/network/auth_storage.dart';
import '../../core/network/dio_client.dart';

const _googleClientId = String.fromEnvironment('GOOGLE_WEB_CLIENT_ID');

final _googleSignIn = GoogleSignIn(
  clientId: _googleClientId.isNotEmpty ? _googleClientId : null,
  scopes: ['email', 'profile'],
);

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
    } catch (_) {
      // Silently ignore — tokens are still valid; user data will reload on next app open.
    }
  }

  Future<void> loginWithGoogle() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      // Sign out any previous session first to force account chooser
      await _googleSignIn.signOut();

      final googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        // User cancelled the picker
        state = state.copyWith(isLoading: false);
        return;
      }

      final googleAuth = await googleUser.authentication;
      final idToken    = googleAuth.idToken;
      final accessToken = googleAuth.accessToken;

      // On web, prefer idToken; fall back to accessToken
      final token = idToken ?? accessToken;
      if (token == null) {
        throw Exception(
          'Google authentication did not return a token. '
          'Make sure the Web Client ID is correctly configured in Google Cloud Console.',
        );
      }

      // Exchange the token for app JWT tokens via the backend
      final res = await _dio.post(
        '/auth/google',
        data: idToken != null
            ? {'id_token': idToken}
            : {'access_token': accessToken},
      );
      final data = res.data['data'] as Map<String, dynamic>;
      await AuthStorage.saveTokens(
        accessToken: data['access_token'] as String,
        refreshToken: data['refresh_token'] as String,
      );
      await _loadMe();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: _parseError(e));
      rethrow;
    }
    state = state.copyWith(isLoading: false);
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
      switch (e.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.receiveTimeout:
        case DioExceptionType.sendTimeout:
          return 'Server is starting up — please wait a moment and try again.';
        case DioExceptionType.connectionError:
          return 'No internet connection. Please check your network and try again.';
        default:
          return e.response?.data?['message'] as String? ??
              e.response?.data?['detail'] as String? ??
              e.message ??
              'Something went wrong. Please try again.';
      }
    }
    return e.toString();
  }
}

final authNotifierProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(dioProvider));
});
