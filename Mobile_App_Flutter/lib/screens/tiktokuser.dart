import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class TikTokUserScraperPage extends StatefulWidget {
  const TikTokUserScraperPage({super.key});

  @override
  State<TikTokUserScraperPage> createState() => _TikTokUserScraperPageState();
}

class _TikTokUserScraperPageState extends State<TikTokUserScraperPage> {
  final String scraperAPI = 'http://namnom.loca.lt';
  final TextEditingController _userIdController = TextEditingController();
  bool _isLoading = false;
  String _status = 'Enter User ID and Press Start';
  List<dynamic> _videos = [];
  Timer? _pollingTimer;
  String _current_search_id = '';

  @override
  void dispose() {
    _userIdController.dispose();
    _pollingTimer?.cancel();
    super.dispose();
  }

  Future<void> _startScraping() async {
    if (_userIdController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a User ID')),
      );
      return;
    }

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
          'search_type': 'userid',
          'search_query': _userIdController.text,
          'max_videos': 5, // Constant value for max videos
        }),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _current_search_id = data['id'];
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
        Uri.parse('$scraperAPI/get-status/?id=$_current_search_id'),
        headers: {
          'bypass-tunnel-reminder': 'true',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
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
        title: const Text('TikTok User Scraper'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _userIdController,
              decoration: const InputDecoration(
                labelText: 'TikTok User ID',
                border: OutlineInputBorder(),
                hintText: 'Enter the TikTok User ID',
              ),
            ),
            const SizedBox(height: 16),
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
                  : const Text('Start Scraping'),
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
              )
                  : ListView.builder(
                itemCount: _videos.length,
                itemBuilder: (context, index) {
                  final video = _videos[index];
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      title: Text(video['userid'] ?? 'Unknown User'),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Song: ${video['song'] ?? 'No song'}'),
                          Text('Likes: ${video['like_count'] ?? 0}'),
                          Text('Comments: ${video['comment_count'] ?? 0}'),
                          Text('Shares: ${video['share_count'] ?? 0}'),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}