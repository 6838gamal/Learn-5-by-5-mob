import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_provider.dart';
import '../../providers/server_status_provider.dart';
import '../../../core/theme/app_theme.dart';

class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);
    final serverStatus = ref.watch(serverStatusProvider);
    final isLoading = authState.isLoading;

    Future<void> signInWithGoogle() async {
      try {
        await ref.read(authNotifierProvider.notifier).loginWithGoogle();
        if (context.mounted) context.go('/home');
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(e.toString()),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 6),
            ),
          );
        }
      }
    }

    return Scaffold(
      backgroundColor: AppThemeData.lightBgColor,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 48),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Logo / icon
                Container(
                  width: 88,
                  height: 88,
                  decoration: BoxDecoration(
                    gradient: AppThemeData.gradientPrimary,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: const Icon(Icons.auto_stories, color: Colors.white, size: 44),
                ),
                const SizedBox(height: 32),

                Text(
                  'Learn 5 by 5',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppThemeData.titleDarkColor,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Learn 5 new words every day',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 32),

                // Server status indicator
                _ServerStatusBadge(status: serverStatus, onRetry: () {
                  ref.read(serverStatusProvider.notifier).retry();
                }),

                const SizedBox(height: 32),

                // Google Sign-In button
                _GoogleSignInButton(
                  onPressed: isLoading ? null : signInWithGoogle,
                  isLoading: isLoading,
                ),

                // Loading hint during auth
                if (isLoading) ...[
                  const SizedBox(height: 24),
                  Text(
                    'Signing in…',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ServerStatusBadge extends StatelessWidget {
  final ServerStatus status;
  final VoidCallback onRetry;

  const _ServerStatusBadge({required this.status, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 400),
      child: switch (status) {
        ServerStatus.checking => _badge(
            key: const ValueKey('checking'),
            color: const Color(0xFFF5F5F5),
            border: const Color(0xFFE0E0E0),
            icon: const SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF9E9E9E)),
            ),
            label: 'Waking up server…',
            labelColor: const Color(0xFF757575),
          ),
        ServerStatus.available => _badge(
            key: const ValueKey('available'),
            color: const Color(0xFFE8F5E9),
            border: const Color(0xFF81C784),
            icon: const Icon(Icons.check_circle_rounded, size: 16, color: Color(0xFF388E3C)),
            label: 'Server is ready',
            labelColor: const Color(0xFF2E7D32),
          ),
        ServerStatus.unavailable => Row(
            key: const ValueKey('unavailable'),
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _badge(
                color: const Color(0xFFFFEBEE),
                border: const Color(0xFFE57373),
                icon: const Icon(Icons.error_rounded, size: 16, color: Color(0xFFC62828)),
                label: 'Server unreachable',
                labelColor: const Color(0xFFC62828),
              ),
              const SizedBox(width: 8),
              GestureDetector(
                onTap: onRetry,
                child: const Text(
                  'Retry',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF5B4FE9),
                    decoration: TextDecoration.underline,
                  ),
                ),
              ),
            ],
          ),
      },
    );
  }

  Widget _badge({
    Key? key,
    required Color color,
    required Color border,
    required Widget icon,
    required String label,
    required Color labelColor,
  }) {
    return Container(
      key: key,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          icon,
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w500,
              color: labelColor,
            ),
          ),
        ],
      ),
    );
  }
}

class _GoogleSignInButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final bool isLoading;

  const _GoogleSignInButton({required this.onPressed, required this.isLoading});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          backgroundColor: Colors.white,
          side: const BorderSide(color: Color(0xFFDADCE0)),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
        child: isLoading
            ? const SizedBox(
                width: 22,
                height: 22,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Google "G" logo drawn with a simple colored circle placeholder
                  _GoogleLogo(),
                  const SizedBox(width: 12),
                  const Text(
                    'Continue with Google',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF3C4043),
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}

class _GoogleLogo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Simple Google "G" rendered with text styling
    return Container(
      width: 22,
      height: 22,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(2),
      ),
      child: const Center(
        child: Text(
          'G',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Color(0xFF4285F4),
            fontFamily: 'sans-serif',
          ),
        ),
      ),
    );
  }
}
