import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/lesson_provider.dart';
import '../../providers/review_provider.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lessonAsync  = ref.watch(todayLessonProvider);
    final reviewAsync  = ref.watch(reviewDueCountProvider);
    final streakAsync  = ref.watch(streakProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Learn 5 by 5'),
        actions: [
          IconButton(icon: const Icon(Icons.notifications_outlined), onPressed: () {}),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(todayLessonProvider);
          ref.invalidate(reviewDueCountProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Streak card
              streakAsync.when(
                data: (streak) => _StreakCard(streak: streak),
                loading: () => const _StreakCard(streak: 0),
                error: (_, __) => const SizedBox.shrink(),
              ),
              const SizedBox(height: 16),

              // Today's lesson
              Text("Today's Lesson", style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              lessonAsync.when(
                data: (lesson) => _LessonCard(lesson: lesson),
                loading: () => const _LoadingCard(),
                error: (e, _) => _ErrorCard(message: e.toString()),
              ),
              const SizedBox(height: 16),

              // Review section
              Text('Review', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              reviewAsync.when(
                data: (count) => _ReviewCard(count: count),
                loading: () => const _LoadingCard(),
                error: (_, __) => const SizedBox.shrink(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StreakCard extends StatelessWidget {
  final int streak;
  const _StreakCard({required this.streak});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF5B4FE9), Color(0xFF7C72F0)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          const Text('🔥', style: TextStyle(fontSize: 36)),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('$streak day streak', style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
              const Text('Keep it up!', style: TextStyle(color: Colors.white70, fontSize: 14)),
            ],
          ),
        ],
      ),
    );
  }
}

class _LessonCard extends StatelessWidget {
  final Map<String, dynamic> lesson;
  const _LessonCard({required this.lesson});

  @override
  Widget build(BuildContext context) {
    final progress = lesson['progress'] as Map<String, dynamic>?;
    final isComplete = progress?['is_complete'] ?? false;
    final step = progress?['step_completed'] ?? 0;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text('📚', style: TextStyle(fontSize: 24)),
                const SizedBox(width: 8),
                Text("5 New Words", style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const Spacer(),
                if (isComplete)
                  const Icon(Icons.check_circle, color: Color(0xFF22C55E))
                else
                  Text('Step $step/11', style: const TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
            const SizedBox(height: 12),
            LinearProgressIndicator(
              value: step / 11,
              borderRadius: BorderRadius.circular(4),
              backgroundColor: const Color(0xFFF3F4F6),
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () => context.go('/lesson'),
              child: Text(step == 0 ? 'Start Today\'s Lesson' : isComplete ? 'Review Lesson' : 'Continue Lesson'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ReviewCard extends StatelessWidget {
  final int count;
  const _ReviewCard({required this.count});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            const Text('🔄', style: TextStyle(fontSize: 24)),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('$count words due', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const Text('Spaced repetition review', style: TextStyle(color: Colors.grey, fontSize: 12)),
                ],
              ),
            ),
            if (count > 0)
              FilledButton.tonal(
                onPressed: () => context.go('/review'),
                child: const Text('Review'),
              ),
          ],
        ),
      ),
    );
  }
}

class _LoadingCard extends StatelessWidget {
  const _LoadingCard();
  @override
  Widget build(BuildContext context) => const Card(child: Padding(padding: EdgeInsets.all(40), child: Center(child: CircularProgressIndicator())));
}

class _ErrorCard extends StatelessWidget {
  final String message;
  const _ErrorCard({required this.message});
  @override
  Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(20), child: Text(message, style: const TextStyle(color: Colors.red))));
}
