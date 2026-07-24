import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

// ─────────────────────────────────────────────
// Design tokens — colours, gradients, typography
// ─────────────────────────────────────────────
class AppThemeData {
  AppThemeData._();

  static const primaryColor   = Color(0xFF5B4FE9);
  static const accentColor    = Color(0xFF7C72F0);
  static const successColor   = Color(0xFF22C55E);
  static const errorColor     = Color(0xFFEF4444);
  static const darkBgColor    = Color(0xFF0F0E1A);
  static const darkCardColor  = Color(0xFF1C1B2E);
  static const lightBgColor   = Color(0xFFF8F9FF);
  static const inputFillColor = Color(0xFFF3F4F6);
  static const titleDarkColor = Color(0xFF1E1B4B);

  static const gradientPrimary = LinearGradient(
    colors: [primaryColor, accentColor],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

// ─────────────────────────────────────────────
// Card decoration constants
// ─────────────────────────────────────────────
class AppCardData {
  AppCardData._();

  static const double borderRadius = 16.0;
  static const EdgeInsets padding  = EdgeInsets.all(20);
  static const double elevation    = 0.0;

  static BoxDecoration lightDecoration() => BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(borderRadius),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withOpacity(0.04),
        blurRadius: 12,
        offset: const Offset(0, 4),
      ),
    ],
  );

  static BoxDecoration darkDecoration() => BoxDecoration(
    color: AppThemeData.darkCardColor,
    borderRadius: BorderRadius.circular(borderRadius),
  );
}

// ─────────────────────────────────────────────
// MaterialApp themes
// ─────────────────────────────────────────────
class AppTheme {
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppThemeData.primaryColor,
      brightness: Brightness.light,
    ),
    fontFamily: 'Inter',
    scaffoldBackgroundColor: AppThemeData.lightBgColor,
    cardTheme: CardThemeData(
      elevation: AppCardData.elevation,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppCardData.borderRadius),
      ),
      color: Colors.white,
    ),
    appBarTheme: const AppBarTheme(
      elevation: 0,
      centerTitle: true,
      backgroundColor: Colors.white,
      foregroundColor: AppThemeData.titleDarkColor,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: AppThemeData.primaryColor,
        foregroundColor: Colors.white,
        minimumSize: const Size(double.infinity, 52),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppThemeData.inputFillColor,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppThemeData.primaryColor, width: 2),
      ),
    ),
  );

  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppThemeData.primaryColor,
      brightness: Brightness.dark,
    ),
    fontFamily: 'Inter',
    scaffoldBackgroundColor: AppThemeData.darkBgColor,
    cardTheme: CardThemeData(
      elevation: AppCardData.elevation,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppCardData.borderRadius),
      ),
      color: AppThemeData.darkCardColor,
    ),
  );
}

// ─────────────────────────────────────────────
// Riverpod provider for theme mode
// ─────────────────────────────────────────────
final themeModeProvider =
    StateNotifierProvider<ThemeModeNotifier, ThemeMode>((ref) {
  return ThemeModeNotifier();
});

class ThemeModeNotifier extends StateNotifier<ThemeMode> {
  ThemeModeNotifier() : super(ThemeMode.system) {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final value = prefs.getString('theme_mode') ?? 'system';
    state = _parse(value);
  }

  Future<void> setMode(ThemeMode mode) async {
    state = mode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('theme_mode', mode.name);
  }

  ThemeMode _parse(String v) => switch (v) {
        'light' => ThemeMode.light,
        'dark'  => ThemeMode.dark,
        _       => ThemeMode.system,
      };
}
