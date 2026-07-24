import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/dio_client.dart';

class AiChatState {
  final String? conversationId;
  final List<Map<String, dynamic>> messages;
  final List<Map<String, dynamic>> lastCorrections;
  final bool isLoading;
  final Map<String, dynamic>? feedback;

  const AiChatState({
    this.conversationId,
    this.messages = const [],
    this.lastCorrections = const [],
    this.isLoading = false,
    this.feedback,
  });

  AiChatState copyWith({
    String? conversationId,
    List<Map<String, dynamic>>? messages,
    List<Map<String, dynamic>>? lastCorrections,
    bool? isLoading,
    Map<String, dynamic>? feedback,
  }) => AiChatState(
    conversationId: conversationId ?? this.conversationId,
    messages: messages ?? this.messages,
    lastCorrections: lastCorrections ?? this.lastCorrections,
    isLoading: isLoading ?? this.isLoading,
    feedback: feedback ?? this.feedback,
  );
}

class AiChatNotifier extends StateNotifier<AiChatState> {
  final Ref _ref;
  AiChatNotifier(this._ref) : super(const AiChatState());

  Future<void> startConversation({int languageId = 1}) async {
    state = state.copyWith(isLoading: true);
    try {
      final dio = _ref.read(dioProvider);
      final res = await dio.post('/ai/conversation/start', data: {'language_id': languageId}, options: null);
      state = state.copyWith(
        conversationId: res.data['data']['conversation_id'] as String,
        isLoading: false,
        messages: [],
      );
    } catch (e) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> endConversation() async {
    final id = state.conversationId;
    if (id == null) return;
    try {
      final dio = _ref.read(dioProvider);
      final res = await dio.post('/ai/conversation/$id/end');
      state = state.copyWith(feedback: res.data['data'] as Map<String, dynamic>, conversationId: null);
    } catch (_) {}
  }
}

final aiChatProvider = StateNotifierProvider<AiChatNotifier, AiChatState>((ref) {
  return AiChatNotifier(ref);
});
