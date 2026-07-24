import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/dio_client.dart';
import 'auth_provider.dart';

final todayLessonProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final dio = ref.watch(dioProvider);
  final user = ref.watch(authNotifierProvider).user;
  final languageId = user != null ? (user as dynamic).targetLanguageId ?? 1 : 1;

  final res = await dio.get('/lessons/today', queryParameters: {'language_id': languageId});
  return res.data['data'] as Map<String, dynamic>;
});

final streakProvider = FutureProvider<int>((ref) async {
  final dio = ref.watch(dioProvider);
  final res = await dio.get('/lessons/streak', queryParameters: {'language_id': 1});
  return (res.data['data']['streak_days'] as num).toInt();
});
