import 'dart:async';
import 'dart:convert';
import 'package:boost_app/widgets/widgets.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class TikTokScraperPage extends StatefulWidget {
  const TikTokScraperPage({super.key});

  @override
  State<TikTokScraperPage> createState() => _TikTokScraperPageState();
}

class _TikTokScraperPageState extends State<TikTokScraperPage> {
  final TextEditingController _queryController = TextEditingController();
  final TextEditingController _maxVideosController = TextEditingController();
  final String scraperAPI = 'http://namnom.loca.lt';
  String _selectedSearchType = 'hashtag';
  bool _isLoading = false;
  String _status = '';
  List<dynamic> _videos = [];
  Timer? _pollingTimer;
  String _current_search_id = '';

  final List<Map<String, String>> searchTypes = [
    {'value': 'hashtag', 'label': 'Hashtag'},
    {'value': 'userid', 'label': 'User ID'},
    {'value': 'trending', 'label': 'Trending'},
    {'value': 'topic', 'label': 'Topic'},
  ];

  @override
  void dispose() {
    _queryController.dispose();
    _maxVideosController.dispose();
    _pollingTimer?.cancel();
    super.dispose();
  }

  Future<void> _startScraping() async {
    if (_queryController.text.isEmpty || _maxVideosController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in all fields')),
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
          'bypass-tunnel-reminder': 'true', // Header for localtunnel
        },
        body: json.encode({
          'search_type': _selectedSearchType,
          'search_query': _queryController.text,
          'max_videos': int.parse(_maxVideosController.text),
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
          'bypass-tunnel-reminder': 'true', // Header for localtunnel
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
        title: const Text('TikTok Scraper'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: SizedBox(
            height: MediaQuery.of(context).size.height,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _selectedSearchType,
                  decoration: const InputDecoration(
                    labelText: 'Search Type',
                    border: OutlineInputBorder(),
                  ),
                  items: searchTypes.map((type) {
                    return DropdownMenuItem(
                      value: type['value'],
                      child: Text(type['label']!),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() => _selectedSearchType = value!);
                  },
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _queryController,
                  decoration: const InputDecoration(
                    labelText: 'Search Query',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _maxVideosController,
                  decoration: const InputDecoration(
                    labelText: 'Max Videos',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 24),
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
                if (_status.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text('Status: $_status'),
                  ),
                const SizedBox(height: 16),
                Expanded(
                  child: _videos.isEmpty
                      ? const Center(
                    child: Text('No videos found'),
                  )
                      : ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
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
                if (_videos.isNotEmpty)
                  SizedBox(
                    height: 400,
                    child: TikTokVideoList(
                        videos: _videos
                    )
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}