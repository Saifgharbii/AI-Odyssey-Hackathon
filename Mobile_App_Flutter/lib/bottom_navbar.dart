import 'package:boost_app/screens/post_creator.dart';
import 'package:boost_app/screens/scrape_page.dart';
import 'package:boost_app/screens/search_page.dart';
import 'package:boost_app/screens/tiktokuser.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'screens/profile_screen.dart';

class BottomNavbar extends StatefulWidget {
  const BottomNavbar({super.key});

  static void switchToPage(BuildContext context, int index) {
    final state = context.findAncestorStateOfType<_HomePageState>();
    if (state != null) {
      state._onItemTapped(index);
    }
  }

  @override
  State<BottomNavbar> createState() => _HomePageState();
}

class _HomePageState extends State<BottomNavbar> {
  int _selectedIndex = 0;
  User? user;
  DateTime? lastPressed;

  late final List<Widget> _pages;
  late final List<Widget> _pageWidgets;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
      for (int i = 0; i < _pageWidgets.length; i++) {
        _pageWidgets[i] = Offstage(
          offstage: _selectedIndex != i,
          child: TickerMode(
            enabled: _selectedIndex == i,
            child: _pages[i],
          ),
        );
      }
    });
  }

  @override
  void initState() {
    super.initState();
    _pages = [
      const TrendingPage(),
      const TikTokUserScraperPage(),
      const MediaProcessingPage(),
      const TikTokScraperPage(),
      const ProfileScreen(),
    ];

    _pageWidgets = _pages.asMap().entries.map((entry) {
      return Offstage(
        offstage: _selectedIndex != entry.key,
        child: TickerMode(
          enabled: _selectedIndex == entry.key,
          child: entry.value,
        ),
      );
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (bool didPop, Object? result) async {
        final now = DateTime.now();
        if (lastPressed == null ||
            now.difference(lastPressed!) > const Duration(seconds: 2)) {
          lastPressed = now;
          Fluttertoast.showToast(msg: 'Tap again to exit');
        } else {
          SystemNavigator.pop();
        }
      },
      child: Scaffold(
        backgroundColor: theme.scaffoldBackgroundColor,
        body: SafeArea(
          child: Column(
            children: [
              // Main content area
              Expanded(
                child: Stack(
                  children: _pageWidgets,
                ),
              ),
              // Navigation bar
              BottomNavigationBar(
                currentIndex: _selectedIndex,
                backgroundColor: theme.cardColor,
                onTap: _onItemTapped,
                selectedItemColor: theme.primaryColor,
                unselectedItemColor: theme.colorScheme.tertiary,
                showSelectedLabels: true,
                showUnselectedLabels: true,
                items: <BottomNavigationBarItem>[
                  BottomNavigationBarItem(
                    icon: Icon(Icons.trending_up_outlined, color: theme.colorScheme.tertiary),
                    activeIcon: Icon(Icons.trending_up_outlined, color: theme.primaryColor),
                    label: "Trending Now",
                  ),
                  BottomNavigationBarItem(
                    icon: Icon(Icons.supervised_user_circle, color: theme.colorScheme.tertiary),
                    activeIcon: Icon(Icons.supervised_user_circle, color: theme.primaryColor),
                    label: "User Data",
                  ),
                  BottomNavigationBarItem(
                    icon: Icon(Icons.post_add, color: theme.colorScheme.tertiary),
                    activeIcon: Icon(Icons.post_add, color: theme.primaryColor),
                    label: "Post Maker",
                  ),
                  BottomNavigationBarItem(
                    icon: Icon(Icons.search, color: theme.colorScheme.tertiary),
                    activeIcon: Icon(Icons.search, color: theme.primaryColor),
                    label: "Scraper",
                  ),
                  BottomNavigationBarItem(
                    icon: Icon(Icons.person, color: theme.colorScheme.tertiary),
                    activeIcon: Icon(Icons.person, color: theme.primaryColor),
                    label: "Profile",
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}