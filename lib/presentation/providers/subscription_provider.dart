import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/dio_client.dart';

final subscriptionPlansProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final dio = ref.watch(dioProvider);
  final res = await dio.get('/subscriptions/plans');
  return (res.data['data']['plans'] as List).cast<Map<String, dynamic>>();
});

final currentSubscriptionProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final dio = ref.watch(dioProvider);
  final res = await dio.get('/subscriptions/current');
  return res.data['data'] as Map<String, dynamic>?;
});
