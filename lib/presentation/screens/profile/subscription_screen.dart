import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/subscription_provider.dart';

class SubscriptionScreen extends ConsumerWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final plansAsync = ref.watch(subscriptionPlansProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Subscription')),
      body: plansAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (plans) => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              const Text('Choose Your Plan', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              const Text('Unlock your full learning potential', style: TextStyle(color: Colors.grey)),
              const SizedBox(height: 24),
              ...plans.map((plan) => _PlanCard(plan: plan)),
            ],
          ),
        ),
      ),
    );
  }
}

class _PlanCard extends StatelessWidget {
  final Map<String, dynamic> plan;
  const _PlanCard({required this.plan});

  @override
  Widget build(BuildContext context) {
    final isPremium = plan['slug'] == 'premium' || plan['slug'] == 'lifetime';

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isPremium ? const Color(0xFF5B4FE9) : const Color(0xFFE5E7EB),
          width: isPremium ? 2 : 1,
        ),
        color: isPremium ? const Color(0xFFF0EFFE) : Colors.white,
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(plan['name'] as String, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const Spacer(),
                Text('\$${plan['price_usd']}', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF5B4FE9))),
                if (plan['billing_period'] != null)
                  Text('/${plan['billing_period']}', style: const TextStyle(color: Colors.grey)),
              ],
            ),
            const SizedBox(height: 12),
            _Feature(label: plan['ai_chat_limit'] == null ? 'Unlimited AI conversations' : '${plan['ai_chat_limit']} AI conversations/day'),
            _Feature(label: plan['lesson_limit'] == null ? 'All lessons unlocked' : '1 lesson/day'),
            if (isPremium) ...[
              const _Feature(label: 'Smart spaced repetition'),
              const _Feature(label: 'Detailed progress reports'),
              const _Feature(label: 'All scenarios'),
            ],
            const SizedBox(height: 16),
            if (isPremium)
              FilledButton(
                onPressed: () {/* TODO: Stripe checkout */},
                child: Text(plan['slug'] == 'lifetime' ? 'Buy Lifetime' : 'Subscribe'),
              )
            else
              FilledButton.tonal(
                onPressed: null,
                child: const Text('Current Plan'),
              ),
          ],
        ),
      ),
    );
  }
}

class _Feature extends StatelessWidget {
  final String label;
  const _Feature({required this.label});
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 6),
    child: Row(children: [
      const Icon(Icons.check, size: 16, color: Color(0xFF22C55E)),
      const SizedBox(width: 8),
      Text(label, style: const TextStyle(fontSize: 13)),
    ]),
  );
}
