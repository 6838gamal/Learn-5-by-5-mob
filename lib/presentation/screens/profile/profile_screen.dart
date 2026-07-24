import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);
    final user = authState.user;

    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Avatar
            const CircleAvatar(radius: 48, backgroundColor: Color(0xFF5B4FE9), child: Icon(Icons.person, size: 48, color: Colors.white)),
            const SizedBox(height: 12),
            Text(user?.fullName ?? 'Learner', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            Text(user?.email ?? '', style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 24),

            // Menu items
            _MenuItem(icon: Icons.settings_outlined, label: 'Settings', onTap: () => context.push('/settings')),
            _MenuItem(icon: Icons.workspace_premium_outlined, label: 'Subscription', onTap: () => context.push('/subscription')),
            _MenuItem(icon: Icons.headset_mic_outlined, label: 'Support', onTap: () => context.push('/support')),
            _MenuItem(icon: Icons.bar_chart_outlined, label: 'Statistics', onTap: () {}),
            const Divider(height: 32),
            _MenuItem(
              icon: Icons.logout,
              label: 'Sign Out',
              color: Colors.red,
              onTap: () async {
                await ref.read(authNotifierProvider.notifier).logout();
                if (context.mounted) context.go('/auth/login');
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _MenuItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final Color? color;

  const _MenuItem({required this.icon, required this.label, required this.onTap, this.color});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: color),
      title: Text(label, style: TextStyle(color: color)),
      trailing: color == null ? const Icon(Icons.chevron_right, color: Colors.grey) : null,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      onTap: onTap,
    );
  }
}
