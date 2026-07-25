class AppConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://learn-5-by-5-api-backend.onrender.com/api/v1',
  );

  // Render.com free tier can take ~20-25 s on cold start — use generous timeouts.
  static const int connectTimeoutMs = 30000;
  static const int receiveTimeoutMs = 60000;

  static const int maxDailyWords = 5;
  static const int quizQuestions = 7;

  static const List<String> supportedLanguageCodes = ['en', 'ar', 'fr', 'es', 'de'];
}
