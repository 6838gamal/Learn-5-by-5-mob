import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/support_provider.dart';

class TicketDetailScreen extends ConsumerStatefulWidget {
  final String ticketId;
  const TicketDetailScreen({super.key, required this.ticketId});
  @override
  ConsumerState<TicketDetailScreen> createState() => _TicketDetailScreenState();
}

class _TicketDetailScreenState extends ConsumerState<TicketDetailScreen> {
  final _msgCtrl = TextEditingController();
  bool _loading = false;

  Future<void> _send() async {
    if (_msgCtrl.text.trim().isEmpty) return;
    setState(() => _loading = true);
    try {
      await ref.read(supportProvider.notifier).sendMessage(widget.ticketId, _msgCtrl.text.trim());
      _msgCtrl.clear();
      ref.invalidate(ticketDetailProvider(widget.ticketId));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final detailAsync = ref.watch(ticketDetailProvider(widget.ticketId));

    return Scaffold(
      appBar: AppBar(title: const Text('Ticket')),
      body: detailAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (detail) {
          final messages = (detail['messages'] as List?) ?? [];
          return Column(
            children: [
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: messages.length,
                  itemBuilder: (ctx, i) {
                    final m = messages[i] as Map<String, dynamic>;
                    final isAdmin = m['sender_type'] == 'admin';
                    return Align(
                      alignment: isAdmin ? Alignment.centerLeft : Alignment.centerRight,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(12),
                        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                        decoration: BoxDecoration(
                          color: isAdmin ? const Color(0xFFF3F4F6) : const Color(0xFF5B4FE9),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Text(m['content'] as String, style: TextStyle(color: isAdmin ? Colors.black87 : Colors.white)),
                      ),
                    );
                  },
                ),
              ),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: const BoxDecoration(
                  color: Colors.white,
                  border: Border(top: BorderSide(color: Color(0xFFE5E7EB))),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _msgCtrl,
                        decoration: const InputDecoration(hintText: 'Type a message...', border: InputBorder.none),
                      ),
                    ),
                    IconButton(
                      icon: _loading ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.send),
                      onPressed: _loading ? null : _send,
                      color: const Color(0xFF5B4FE9),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
