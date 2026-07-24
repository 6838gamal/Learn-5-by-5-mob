import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});
  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final PageController _pageCtrl = PageController();
  int _page = 0;

  // Selections
  String? _targetLang;
  String? _uiLang;
  String? _level;

  static const _langs = [
    {'code': 'en', 'name': 'English', 'flag': '🇬🇧'},
    {'code': 'ar', 'name': 'العربية', 'flag': '🇸🇦'},
    {'code': 'fr', 'name': 'Français', 'flag': '🇫🇷'},
    {'code': 'es', 'name': 'Español', 'flag': '🇪🇸'},
    {'code': 'de', 'name': 'Deutsch', 'flag': '🇩🇪'},
  ];

  static const _levels = [
    {'key': 'beginner',     'label': 'Beginner',     'desc': 'I\'m just starting out'},
    {'key': 'intermediate', 'label': 'Intermediate', 'desc': 'I know some basics'},
    {'key': 'advanced',     'label': 'Advanced',     'desc': 'I want to refine my skills'},
  ];

  void _next() {
    if (_page < 2) {
      _pageCtrl.nextPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
    } else {
      // TODO: save preferences via provider, then navigate
      context.go('/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Progress indicator
            Padding(
              padding: const EdgeInsets.all(24),
              child: Row(
                children: List.generate(3, (i) => Expanded(
                  child: Container(
                    height: 4,
                    margin: const EdgeInsets.symmetric(horizontal: 3),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(2),
                      color: i <= _page ? const Color(0xFF5B4FE9) : const Color(0xFFE5E7EB),
                    ),
                  ),
                )),
              ),
            ),

            Expanded(
              child: PageView(
                controller: _pageCtrl,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (p) => setState(() => _page = p),
                children: [
                  // Page 1: Target language
                  _LanguagePicker(
                    title: 'What do you want to learn?',
                    langs: _langs,
                    selected: _targetLang,
                    onSelect: (c) => setState(() => _targetLang = c),
                  ),
                  // Page 2: UI language
                  _LanguagePicker(
                    title: 'What\'s your interface language?',
                    langs: _langs,
                    selected: _uiLang,
                    onSelect: (c) => setState(() => _uiLang = c),
                  ),
                  // Page 3: Level
                  _LevelPicker(
                    levels: _levels,
                    selected: _level,
                    onSelect: (k) => setState(() => _level = k),
                  ),
                ],
              ),
            ),

            Padding(
              padding: const EdgeInsets.all(24),
              child: FilledButton(
                onPressed: (_page == 0 && _targetLang == null) || (_page == 1 && _uiLang == null) || (_page == 2 && _level == null)
                    ? null
                    : _next,
                child: Text(_page == 2 ? 'Start Learning' : 'Continue'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LanguagePicker extends StatelessWidget {
  final String title;
  final List<Map<String, String>> langs;
  final String? selected;
  final ValueChanged<String> onSelect;

  const _LanguagePicker({required this.title, required this.langs, this.selected, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          ...langs.map((l) => _Tile(
            leading: Text(l['flag']!, style: const TextStyle(fontSize: 28)),
            label: l['name']!,
            selected: selected == l['code'],
            onTap: () => onSelect(l['code']!),
          )),
        ],
      ),
    );
  }
}

class _LevelPicker extends StatelessWidget {
  final List<Map<String, String>> levels;
  final String? selected;
  final ValueChanged<String> onSelect;

  const _LevelPicker({required this.levels, this.selected, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('What\'s your level?', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          ...levels.map((l) => _Tile(
            leading: null,
            label: l['label']!,
            subtitle: l['desc'],
            selected: selected == l['key'],
            onTap: () => onSelect(l['key']!),
          )),
        ],
      ),
    );
  }
}

class _Tile extends StatelessWidget {
  final Widget? leading;
  final String label;
  final String? subtitle;
  final bool selected;
  final VoidCallback onTap;

  const _Tile({this.leading, required this.label, this.subtitle, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: selected ? const Color(0xFF5B4FE9) : const Color(0xFFE5E7EB),
            width: selected ? 2 : 1,
          ),
          color: selected ? const Color(0xFFF0EFFE) : Colors.white,
        ),
        child: Row(
          children: [
            if (leading != null) ...[leading!, const SizedBox(width: 12)],
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: TextStyle(fontWeight: FontWeight.w600, color: selected ? const Color(0xFF5B4FE9) : null)),
                  if (subtitle != null) Text(subtitle!, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
            ),
            if (selected) const Icon(Icons.check_circle, color: Color(0xFF5B4FE9)),
          ],
        ),
      ),
    );
  }
}
