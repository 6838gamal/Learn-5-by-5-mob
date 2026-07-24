import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/lesson_provider.dart';

/// The 11-step daily lesson flow.
class LessonScreen extends ConsumerStatefulWidget {
  const LessonScreen({super.key});
  @override
  ConsumerState<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends ConsumerState<LessonScreen> {
  int _step = 0;      // current step index (0-10)
  int _wordIndex = 0; // which of the 5 words we're on

  static const _stepTitles = [
    'Word Introduction',
    'Pronunciation',
    'Examples',
    'Daily Sentences',
    'Scenario',
    'AI Conversation',
    'AI Feedback',
    'Quiz',
    'Results',
  ];

  void _nextStep() {
    if (_step < 8) {
      setState(() => _step++);
    } else {
      context.go('/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final lessonAsync = ref.watch(todayLessonProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(_step < _stepTitles.length ? _stepTitles[_step] : ''),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(4),
          child: LinearProgressIndicator(value: (_step + 1) / 9, borderRadius: BorderRadius.circular(2)),
        ),
      ),
      body: lessonAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (lesson) {
          final words = lesson['words'] as List? ?? [];
          return _LessonStepContent(
            step: _step,
            words: words,
            wordIndex: _wordIndex,
            onNext: _nextStep,
            onNextWord: () {
              if (_wordIndex < words.length - 1) {
                setState(() => _wordIndex++);
              } else {
                _nextStep();
              }
            },
          );
        },
      ),
    );
  }
}

class _LessonStepContent extends StatelessWidget {
  final int step;
  final List words;
  final int wordIndex;
  final VoidCallback onNext;
  final VoidCallback onNextWord;

  const _LessonStepContent({
    required this.step, required this.words, required this.wordIndex,
    required this.onNext, required this.onNextWord,
  });

  @override
  Widget build(BuildContext context) {
    final word = words.isNotEmpty ? words[wordIndex] as Map<String, dynamic> : null;

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Expanded(child: _buildStepContent(context, word)),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: step == 0 ? onNextWord : onNext,
            child: Text(step == 0 && wordIndex < words.length - 1 ? 'Next Word' : 'Continue'),
          ),
        ],
      ),
    );
  }

  Widget _buildStepContent(BuildContext context, Map<String, dynamic>? word) {
    return switch (step) {
      0 => word == null
          ? const Center(child: Text('No words loaded'))
          : _WordCard(word: word, wordIndex: wordIndex, total: words.length),
      5 => const _AiChatPlaceholder(),
      7 => const _QuizPlaceholder(),
      _ => Center(
          child: Text('Step ${step + 1}', style: Theme.of(context).textTheme.headlineMedium),
        ),
    };
  }
}

class _WordCard extends StatelessWidget {
  final Map<String, dynamic> word;
  final int wordIndex;
  final int total;

  const _WordCard({required this.word, required this.wordIndex, required this.total});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text('${wordIndex + 1} of $total', style: const TextStyle(color: Colors.grey, fontSize: 14)),
        const SizedBox(height: 24),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: const Color(0xFFF0EFFE),
            borderRadius: BorderRadius.circular(24),
          ),
          child: Column(
            children: [
              Text(word['word'] ?? '', style: const TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: Color(0xFF5B4FE9))),
              if (word['phonetic'] != null) ...[
                const SizedBox(height: 8),
                Text(word['phonetic'], style: const TextStyle(color: Colors.grey, fontSize: 16)),
              ],
              if (word['part_of_speech'] != null) ...[
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF5B4FE9),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(word['part_of_speech'], style: const TextStyle(color: Colors.white, fontSize: 12)),
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: 24),
        IconButton.filled(
          icon: const Icon(Icons.volume_up),
          onPressed: () {/* TODO: play audio */},
          style: IconButton.styleFrom(backgroundColor: const Color(0xFF5B4FE9), foregroundColor: Colors.white, iconSize: 28, minimumSize: const Size(56, 56)),
        ),
        const SizedBox(height: 16),
        Text(word['translation'] ?? '', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w500)),
      ],
    );
  }
}

class _AiChatPlaceholder extends StatelessWidget {
  const _AiChatPlaceholder();
  @override
  Widget build(BuildContext context) => const Center(child: Column(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      Icon(Icons.mic, size: 64, color: Color(0xFF5B4FE9)),
      SizedBox(height: 16),
      Text('AI Conversation', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
      SizedBox(height: 8),
      Text('Practice speaking with AI using today\'s words', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
    ],
  ));
}

class _QuizPlaceholder extends StatelessWidget {
  const _QuizPlaceholder();
  @override
  Widget build(BuildContext context) => const Center(child: Column(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      Icon(Icons.quiz_outlined, size: 64, color: Color(0xFF5B4FE9)),
      SizedBox(height: 16),
      Text('Quiz Time', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
      SizedBox(height: 8),
      Text('Test your knowledge of today\'s words', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
    ],
  ));
}
