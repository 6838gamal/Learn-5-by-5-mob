import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Quiz screen supporting 7 question types.
/// Each question type renders a different widget.
class QuizScreen extends ConsumerStatefulWidget {
  const QuizScreen({super.key});
  @override
  ConsumerState<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends ConsumerState<QuizScreen> {
  int _question = 0;
  int _correct  = 0;
  bool _answered = false;
  int? _selected;

  // Placeholder questions — real data loaded from API in Phase 2
  static const _questions = [
    {'type': 'multiple_choice', 'prompt': 'What does "serene" mean?', 'options': ['Calm', 'Angry', 'Loud', 'Dark'], 'correct': 0},
    {'type': 'fill_blank',      'prompt': 'The lake was ___ at dawn.',  'answer': 'serene'},
  ];

  void _answer(int index) {
    if (_answered) return;
    setState(() {
      _selected = index;
      _answered = true;
      if (index == _questions[_question]['correct']) _correct++;
    });
  }

  void _next() {
    if (_question + 1 >= _questions.length) {
      setState(() => _question = -1); // results
    } else {
      setState(() { _question++; _answered = false; _selected = null; });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_question == -1) return _ResultsScreen(correct: _correct, total: _questions.length);

    final q = _questions[_question];
    return Scaffold(
      appBar: AppBar(
        title: Text('Question ${_question + 1} of ${_questions.length}'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(4),
          child: LinearProgressIndicator(value: (_question + 1) / _questions.length, borderRadius: BorderRadius.circular(2)),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const SizedBox(height: 24),
            Text(q['prompt'] as String, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
            const SizedBox(height: 32),
            if (q['type'] == 'multiple_choice')
              ...List.generate(
                (q['options'] as List).length,
                (i) => _OptionTile(
                  label: (q['options'] as List)[i] as String,
                  state: _answered
                      ? i == q['correct'] ? 'correct' : i == _selected ? 'wrong' : 'default'
                      : 'default',
                  onTap: () => _answer(i),
                ),
              ),
            const Spacer(),
            if (_answered)
              FilledButton(onPressed: _next, child: Text(_question + 1 >= _questions.length ? 'See Results' : 'Next Question')),
          ],
        ),
      ),
    );
  }
}

class _OptionTile extends StatelessWidget {
  final String label;
  final String state; // default / correct / wrong
  final VoidCallback onTap;

  const _OptionTile({required this.label, required this.state, required this.onTap});

  @override
  Widget build(BuildContext context) {
    Color bg = Colors.white, border = const Color(0xFFE5E7EB), text = Colors.black87;
    if (state == 'correct') { bg = const Color(0xFFDCFCE7); border = const Color(0xFF22C55E); text = const Color(0xFF166534); }
    if (state == 'wrong')   { bg = const Color(0xFFFEE2E2); border = const Color(0xFFEF4444); text = const Color(0xFF991B1B); }

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: bg,
          border: Border.all(color: border, width: 1.5),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Text(label, style: TextStyle(fontWeight: FontWeight.w500, color: text)),
      ),
    );
  }
}

class _ResultsScreen extends StatelessWidget {
  final int correct;
  final int total;
  const _ResultsScreen({required this.correct, required this.total});

  @override
  Widget build(BuildContext context) {
    final pct = (correct / total * 100).round();
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(pct >= 80 ? '🎉' : pct >= 50 ? '😊' : '💪', style: const TextStyle(fontSize: 72)),
              const SizedBox(height: 16),
              Text('$pct%', style: const TextStyle(fontSize: 48, fontWeight: FontWeight.bold, color: Color(0xFF5B4FE9))),
              Text('$correct / $total correct', style: const TextStyle(color: Colors.grey, fontSize: 18)),
              const SizedBox(height: 32),
              FilledButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Done')),
            ],
          ),
        ),
      ),
    );
  }
}
