import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/support_provider.dart';

class SupportTicketsScreen extends ConsumerWidget {
  const SupportTicketsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ticketsAsync = ref.watch(supportTicketsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Support'),
        actions: [
          IconButton(icon: const Icon(Icons.add), onPressed: () => context.push('/support/new')),
        ],
      ),
      body: ticketsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (tickets) => tickets.isEmpty
            ? const Center(child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.support_agent_outlined, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('No support tickets', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text('Tap + to create a new ticket', style: TextStyle(color: Colors.grey)),
                ],
              ))
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: tickets.length,
                itemBuilder: (ctx, i) {
                  final t = tickets[i] as Map<String, dynamic>;
                  return Card(
                    margin: const EdgeInsets.only(bottom: 12),
                    child: ListTile(
                      title: Text(t['subject'] as String, maxLines: 1, overflow: TextOverflow.ellipsis),
                      subtitle: Text(t['status'] as String),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => context.push('/support/${t['id']}'),
                    ),
                  );
                },
              ),
      ),
    );
  }
}
