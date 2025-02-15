import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../widgets/widgets.dart';

class TrendingPage extends StatefulWidget {
  const TrendingPage({super.key});

  @override
  State<TrendingPage> createState() => _TrendingPageState();
}

class _TrendingPageState extends State<TrendingPage> {
  final String scraperAPI = 'http://namnom.loca.lt';
  bool _isLoading = false;
  String _status = 'Press Start to Begin';
  List<dynamic> _videos = [];
  Timer? _pollingTimer;

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  Future<void> _startScraping() async {
    setState(() {
      _isLoading = true;
      _status = 'Starting...';
      _videos = [];
    });

    try {
      final response = await http.post(
        Uri.parse('$scraperAPI/scrape-and-download/'),
        headers: {
          'Content-Type': 'application/json',
          'bypass-tunnel-reminder': 'true',
        },
        body: json.encode({
          'search_type': 'topic',
          'search_query': '0',
          'max_videos': 10,
        }),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _startPolling();
      } else {
        setState(() {
          _status = 'Failed to start scraping';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _status = 'Error: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  void _startPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      _checkStatus();
    });
  }

  Future<void> _checkStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$scraperAPI/get-status/?id=test'),
        headers: {
          'bypass-tunnel-reminder': 'true',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          print(data);
          _status = data['status'];
          if (data['videos'] != null) {
            _videos = data['videos'];
          }
        });

        if (data['status'] == 'completed' || data['status'] == 'failed') {
          _pollingTimer?.cancel();
          setState(() => _isLoading = false);
        }
      }
    } catch (e) {
      _pollingTimer?.cancel();
      setState(() {
        _status = 'Error checking status: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TikTok Scraper'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ElevatedButton(
              onPressed: _isLoading ? null : _startScraping,
              child: _isLoading
                  ? const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 8),
                  Text('Processing...'),
                ],
              )
                  : const Text('Start'),
            ),
            const SizedBox(height: 16),
            Text(
              _status,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: _isLoading ? Colors.blue : Colors.black,
                fontWeight: _isLoading ? FontWeight.bold : FontWeight.normal,
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: _videos.isEmpty
                  ? const Center(
                child: Text('No videos found'),
              ) :
                  SizedBox(
                  height: 400,
                  child: TikTokVideoList(
                      videos: _videos
                  )
              ),
            ),
          ],
        ),
      ),
    );
  }
}