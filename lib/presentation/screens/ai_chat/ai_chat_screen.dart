import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/ai_chat_provider.dart';

class AiChatScreen extends ConsumerStatefulWidget {
  const AiChatScreen({super.key});
  @override
  ConsumerState<AiChatScreen> createState() => _AiChatScreenState();
}

class _AiChatScreenState extends ConsumerState<AiChatScreen> {
  bool _isRecording = false;
  bool _isLoading   = false;

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      setState(() { _isRecording = false; _isLoading = true; });
      // TODO: stop recording, send audio to provider, receive reply
      await Future.delayed(const Duration(seconds: 1));
      setState(() => _isLoading = false);
    } else {
      setState(() => _isRecording = true);
      // TODO: start recording
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(aiChatProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Practice'),
        actions: [
          if (state.conversationId != null)
            TextButton(
              onPressed: () => ref.read(aiChatProvider.notifier).endConversation(),
              child: const Text('End'),
            ),
        ],
      ),
      body: Column(
        children: [
          // Scenario banner
          if (state.conversationId == null)
            Expanded(
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.mic, size: 80, color: Color(0xFF5B4FE9)),
                      const SizedBox(height: 24),
                      const Text('AI Conversation', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 12),
                      const Text(
                        'Practice speaking with an AI tutor using today\'s words. Get real-time corrections and feedback.',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey),
                      ),
                      const SizedBox(height: 32),
                      FilledButton.icon(
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('Start Conversation'),
                        onPressed: () => ref.read(aiChatProvider.notifier).startConversation(),
                      ),
                    ],
                  ),
                ),
              ),
            )
          else ...[
            // Message list
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: state.messages.length,
                itemBuilder: (ctx, i) {
                  final msg = state.messages[i];
                  final isUser = msg['role'] == 'user';
                  return _ChatBubble(message: msg, isUser: isUser);
                },
              ),
            ),

            // Corrections strip
            if (state.lastCorrections.isNotEmpty)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                color: const Color(0xFFFFFBEB),
                child: Text(
                  '💡 ${state.lastCorrections.first['corrected'] ?? ''}',
                  style: const TextStyle(color: Color(0xFF92400E), fontSize: 13),
                ),
              ),

            // Mic button
            Padding(
              padding: const EdgeInsets.all(24),
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : GestureDetector(
                      onTap: _toggleRecording,
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        width: _isRecording ? 80 : 64,
                        height: _isRecording ? 80 : 64,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: _isRecording ? const Color(0xFFEF4444) : const Color(0xFF5B4FE9),
                          boxShadow: _isRecording ? [BoxShadow(color: const Color(0xFFEF4444).withOpacity(0.4), blurRadius: 20, spreadRadius: 4)] : [],
                        ),
                        child: Icon(_isRecording ? Icons.stop : Icons.mic, color: Colors.white, size: _isRecording ? 36 : 28),
                      ),
                    ),
            ),
          ],
        ],
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  final Map<String, dynamic> message;
  final bool isUser;

  const _ChatBubble({required this.message, required this.isUser});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        decoration: BoxDecoration(
          color: isUser ? const Color(0xFF5B4FE9) : const Color(0xFFF3F4F6),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(18),
            topRight: const Radius.circular(18),
            bottomLeft: isUser ? const Radius.circular(18) : const Radius.circular(4),
            bottomRight: isUser ? const Radius.circular(4) : const Radius.circular(18),
          ),
        ),
        child: Text(
          message['content'] as String? ?? '',
          style: TextStyle(color: isUser ? Colors.white : Colors.black87),
        ),
      ),
    );
  }
}
