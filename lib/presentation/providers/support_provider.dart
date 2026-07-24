import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/dio_client.dart';

final supportTicketsProvider = FutureProvider<List>((ref) async {
  final dio = ref.watch(dioProvider);
  final res = await dio.get('/support/tickets');
  return res.data['data']['tickets'] as List;
});

final ticketDetailProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, id) async {
  final dio = ref.watch(dioProvider);
  final res = await dio.get('/support/tickets/$id');
  return res.data['data'] as Map<String, dynamic>;
});

class SupportNotifier extends StateNotifier<void> {
  final Ref _ref;
  SupportNotifier(this._ref) : super(null);

  Future<void> createTicket({required String subject, required String category, required String description}) async {
    final dio = _ref.read(dioProvider);
    await dio.post('/support/tickets', data: {'subject': subject, 'category': category, 'description': description});
    _ref.invalidate(supportTicketsProvider);
  }

  Future<void> sendMessage(String ticketId, String content) async {
    final dio = _ref.read(dioProvider);
    await dio.post('/support/tickets/$ticketId/messages', data: {'content': content});
  }
}

final supportProvider = StateNotifierProvider<SupportNotifier, void>((ref) {
  return SupportNotifier(ref);
});
