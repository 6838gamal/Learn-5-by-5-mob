class AppConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  static const int connectTimeoutMs = 15000;
  static const int receiveTimeoutMs = 30000;

  static const int maxDailyWords = 5;
  static const int quizQuestions = 7;

  static const List<String> supportedLanguageCodes = ['en', 'ar', 'fr', 'es', 'de'];
}
