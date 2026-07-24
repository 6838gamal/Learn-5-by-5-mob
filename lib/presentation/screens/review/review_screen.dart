import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/review_provider.dart';

class ReviewScreen extends ConsumerStatefulWidget {
  const ReviewScreen({super.key});
  @override
  ConsumerState<ReviewScreen> createState() => _ReviewScreenState();
}

class _ReviewScreenState extends ConsumerState<ReviewScreen> {
  bool _revealed = false;
  int _currentIndex = 0;

  void _rate(int quality) {
    // TODO: call review provider to record quality rating
    setState(() {
      _revealed = false;
      _currentIndex++;
    });
  }

  @override
  Widget build(BuildContext context) {
    final dueAsync = ref.watch(reviewDueWordsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Review')),
      body: dueAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (words) {
          if (words.isEmpty || _currentIndex >= words.length) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('🎉', style: TextStyle(fontSize: 64)),
                  const SizedBox(height: 16),
                  const Text('All caught up!', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  const Text('No more words due for review today.', style: TextStyle(color: Colors.grey)),
                ],
              ),
            );
          }

          final word = words[_currentIndex] as Map<String, dynamic>;

          return Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                // Progress
                Text('${_currentIndex + 1} / ${words.length}', style: const TextStyle(color: Colors.grey)),
                LinearProgressIndicator(
                  value: (_currentIndex + 1) / words.length,
                  borderRadius: BorderRadius.circular(2),
                ),
                const SizedBox(height: 32),

                // Flashcard
                GestureDetector(
                  onTap: () => setState(() => _revealed = true),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    width: double.infinity,
                    padding: const EdgeInsets.all(40),
                    decoration: BoxDecoration(
                      color: _revealed ? const Color(0xFFF0EFFE) : const Color(0xFF5B4FE9),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: Column(
                      children: [
                        Text(
                          word['word'] ?? '',
                          style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: _revealed ? const Color(0xFF5B4FE9) : Colors.white),
                        ),
                        if (_revealed) ...[
                          const SizedBox(height: 16),
                          const Divider(),
                          const SizedBox(height: 16),
                          Text(word['translation'] ?? '', style: const TextStyle(fontSize: 18)),
                        ] else ...[
                          const SizedBox(height: 16),
                          const Text('Tap to reveal', style: TextStyle(color: Colors.white60, fontSize: 14)),
                        ],
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 32),

                // Rating buttons (SM-2: 0=fail, 3=good, 5=perfect)
                if (_revealed) ...[
                  const Text('How well did you remember it?', style: TextStyle(fontWeight: FontWeight.w500)),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(child: _RateButton(label: '😕 Forgot', color: Colors.red, onTap: () => _rate(0))),
                      const SizedBox(width: 8),
                      Expanded(child: _RateButton(label: '😐 Hard', color: Colors.orange, onTap: () => _rate(2))),
                      const SizedBox(width: 8),
                      Expanded(child: _RateButton(label: '🙂 Good', color: Colors.blue, onTap: () => _rate(4))),
                      const SizedBox(width: 8),
                      Expanded(child: _RateButton(label: '😄 Easy', color: Colors.green, onTap: () => _rate(5))),
                    ],
                  ),
                ] else
                  const Text('Tap the card to reveal the answer', style: TextStyle(color: Colors.grey)),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _RateButton extends StatelessWidget {
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _RateButton({required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onTap,
      style: ElevatedButton.styleFrom(
        backgroundColor: color.withOpacity(0.12),
        foregroundColor: color,
        elevation: 0,
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: Text(label, style: const TextStyle(fontSize: 12)),
    );
  }
}
