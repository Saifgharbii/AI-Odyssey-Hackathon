part of 'widgets.dart';

class TikTokVideoCard extends StatelessWidget {
  final Map<String, dynamic> videoData;

  const TikTokVideoCard({
    super.key,
    required this.videoData,
  });

  Future<void> _launchTikTok() async {
    final Uri url = Uri.parse(videoData['videotiktok']);
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      throw Exception('Could not launch $url');
    }
  }

  String _formatCount(String count) {
    // double number = double.parse(count.replaceAll('K', ''));
    // if (count.contains('K')) {
    //   number *= 1000;
    // }
    // if (number >= 1000000) {
    //   return '${(number / 1000000).toStringAsFixed(1)}M';
    // } else if (number >= 1000) {
    //   return '${(number / 1000).toStringAsFixed(1)}K';
    // }
    return count;
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // User info header
          ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.grey[200],
              child: Text(
                videoData['userid'].substring(1)[0].toUpperCase(),
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
            title: Text(
              videoData['userid'],
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Text(videoData['song']),
          ),
          // Video thumbnail and play button
          InkWell(
            onTap: _launchTikTok,
            child: Stack(
              alignment: Alignment.center,
              children: [
                Container(
                  height: 400,
                  width: double.infinity,
                  color: Colors.black87,
                  child: const Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.play_circle_fill,
                        size: 64,
                        color: Colors.white,
                      ),
                      SizedBox(height: 16),
                      Text(
                        'Watch on TikTok',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          // Engagement metrics
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildEngagementMetric(
                  Icons.favorite,
                  _formatCount(videoData['like_count']),
                  'Likes',
                ),
                _buildEngagementMetric(
                  Icons.comment,
                  _formatCount(videoData['comment_count']),
                  'Comments',
                ),
                _buildEngagementMetric(
                  Icons.share,
                  _formatCount(videoData['share_count']),
                  'Shares',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEngagementMetric(IconData icon, String count, String label) {
    return Column(
      children: [
        Icon(icon, color: Colors.grey[600]),
        const SizedBox(height: 4),
        Text(
          count,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}

// List widget to display multiple videos
class TikTokVideoList extends StatelessWidget {
  final List<dynamic> videos;

  const TikTokVideoList({
    super.key,
    required this.videos,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: videos.length,
      itemBuilder: (context, index) {
        return TikTokVideoCard(
          videoData: videos[index],
        );
      },
    );
  }
}