import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../presentation/screens/auth/login_screen.dart';
import '../../presentation/screens/auth/register_screen.dart';
import '../../presentation/screens/auth/forgot_password_screen.dart';
import '../../presentation/screens/onboarding/onboarding_screen.dart';
import '../../presentation/screens/home/home_screen.dart';
import '../../presentation/screens/lesson/lesson_screen.dart';
import '../../presentation/screens/review/review_screen.dart';
import '../../presentation/screens/quiz/quiz_screen.dart';
import '../../presentation/screens/ai_chat/ai_chat_screen.dart';
import '../../presentation/screens/profile/profile_screen.dart';
import '../../presentation/screens/profile/settings_screen.dart';
import '../../presentation/screens/profile/subscription_screen.dart';
import '../../presentation/screens/support/support_tickets_screen.dart';
import '../../presentation/screens/support/ticket_detail_screen.dart';
import '../../presentation/screens/support/create_ticket_screen.dart';
import '../network/auth_storage.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/home',
    redirect: (context, state) async {
      final isLoggedIn = await AuthStorage.hasToken();
      final onAuthPage = state.matchedLocation.startsWith('/auth');
      final onOnboarding = state.matchedLocation == '/onboarding';

      if (!isLoggedIn && !onAuthPage) return '/auth/login';
      if (isLoggedIn && onAuthPage) return '/home';
      return null;
    },
    routes: [
      // Auth
      GoRoute(path: '/auth/login',          builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/auth/register',       builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/auth/forgot',         builder: (_, __) => const ForgotPasswordScreen()),

      // Onboarding
      GoRoute(path: '/onboarding',          builder: (_, __) => const OnboardingScreen()),

      // Main shell
      ShellRoute(
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(path: '/home',            builder: (_, __) => const HomeScreen()),
          GoRoute(path: '/lesson',          builder: (_, __) => const LessonScreen()),
          GoRoute(path: '/review',          builder: (_, __) => const ReviewScreen()),
          GoRoute(path: '/quiz',            builder: (_, __) => const QuizScreen()),
          GoRoute(path: '/ai-chat',         builder: (_, __) => const AiChatScreen()),
          GoRoute(path: '/profile',         builder: (_, __) => const ProfileScreen()),
          GoRoute(path: '/settings',        builder: (_, __) => const SettingsScreen()),
          GoRoute(path: '/subscription',    builder: (_, __) => const SubscriptionScreen()),
          GoRoute(path: '/support',         builder: (_, __) => const SupportTicketsScreen()),
          GoRoute(path: '/support/new',     builder: (_, __) => const CreateTicketScreen()),
          GoRoute(
            path: '/support/:id',
            builder: (_, state) => TicketDetailScreen(ticketId: state.pathParameters['id']!),
          ),
        ],
      ),
    ],
  );
});

/// Bottom nav shell wrapper.
class MainShell extends StatelessWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined),    selectedIcon: Icon(Icons.home),    label: 'Home'),
          NavigationDestination(icon: Icon(Icons.refresh_outlined),  selectedIcon: Icon(Icons.refresh), label: 'Review'),
          NavigationDestination(icon: Icon(Icons.mic_outlined),      selectedIcon: Icon(Icons.mic),     label: 'Practice'),
          NavigationDestination(icon: Icon(Icons.person_outline),    selectedIcon: Icon(Icons.person),  label: 'Profile'),
        ],
        onDestinationSelected: (index) {
          switch (index) {
            case 0: context.go('/home');
            case 1: context.go('/review');
            case 2: context.go('/ai-chat');
            case 3: context.go('/profile');
          }
        },
      ),
    );
  }
}
