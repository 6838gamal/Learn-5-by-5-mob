import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/dio_client.dart';

final reviewDueWordsProvider = FutureProvider<List>((ref) async {
  final dio = ref.watch(dioProvider);
  final res = await dio.get('/review/due');
  return res.data['data']['words'] as List;
});

final reviewDueCountProvider = FutureProvider<int>((ref) async {
  final dio = ref.watch(dioProvider);
  final res = await dio.get('/review/count');
  return (res.data['data']['count'] as num).toInt();
});
